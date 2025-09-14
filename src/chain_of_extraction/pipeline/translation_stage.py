"""Translation stage for the extraction pipeline."""

from typing import Any, Dict, List
import logging
from .base import PipelineStage
from ..services.llm_service import LLMService
from ..models.document_models import PipelineConfig, TranslationResult, ExtractedRegulation


logger = logging.getLogger(__name__)


class TranslationStage(PipelineStage):
    """Pipeline stage for translating extracted regulation data."""
    
    def __init__(self, config: PipelineConfig):
        super().__init__("Translation", config.__dict__)
        self.llm_service = LLMService()
        self.target_languages = config.target_languages
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate the structured regulation data to target languages."""
        structured_regulation = data.get("structured_regulation")
        result = data["result"]
        
        if not structured_regulation:
            self.logger.warning("No structured regulation data to translate")
            return data
        
        try:
            self.logger.info(f"Starting translation to {len(self.target_languages)} languages")
            
            # Perform translations
            translations = []
            source_language = structured_regulation.language or "auto"
            
            for target_lang in self.target_languages:
                if target_lang != source_language:
                    self.logger.info(f"Translating to {target_lang}")
                    
                    translated_regulation = await self._translate_regulation(
                        structured_regulation, target_lang, source_language
                    )
                    
                    translation_result = TranslationResult(
                        original_language=source_language,
                        target_language=target_lang,
                        translated_regulation=translated_regulation,
                        translation_confidence=0.85  # Default confidence
                    )
                    
                    translations.append(translation_result)
            
            # Update result with translations
            result.translations = translations
            
            self.logger.info(f"Translation completed for {len(translations)} languages")
            
            # Pass data to next stage (or final output)
            data["translations"] = translations
            data["result"] = result
            
            return data
            
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            raise
    
    async def _translate_regulation(
        self, 
        regulation: ExtractedRegulation, 
        target_language: str,
        source_language: str
    ) -> ExtractedRegulation:
        """Translate a regulation to target language."""
        
        # Create a copy of the regulation for translation
        translated_data = regulation.model_dump()
        translated_data["language"] = target_language
        
        # Translate text fields
        text_fields = ["title", "regulation_number", "effective_date", "issuing_authority"]
        for field in text_fields:
            if translated_data.get(field):
                translated_data[field] = self.llm_service.translate_text(
                    translated_data[field], target_language, source_language
                )
        
        # Translate ingredient lists
        list_fields = ["prohibited_ingredients", "permitted_ingredients"]
        for field in list_fields:
            if translated_data.get(field):
                translated_data[field] = [
                    self.llm_service.translate_text(item, target_language, source_language)
                    for item in translated_data[field]
                ]
        
        # Translate restricted ingredients
        if translated_data.get("restricted_ingredients"):
            translated_restricted = []
            for item in translated_data["restricted_ingredients"]:
                translated_item = {
                    "ingredient": self.llm_service.translate_text(
                        item["ingredient"], target_language, source_language
                    ),
                    "restriction": self.llm_service.translate_text(
                        item["restriction"], target_language, source_language
                    )
                }
                translated_restricted.append(translated_item)
            translated_data["restricted_ingredients"] = translated_restricted
        
        # Translate requirement lists
        requirement_fields = [
            "labeling_requirements", "testing_requirements", 
            "packaging_requirements", "penalties", "exemptions"
        ]
        for field in requirement_fields:
            if translated_data.get(field):
                translated_data[field] = [
                    self.llm_service.translate_text(item, target_language, source_language)
                    for item in translated_data[field]
                ]
        
        return ExtractedRegulation(**translated_data)
    
    def validate_input(self, data: Any) -> bool:
        """Validate input has structured regulation."""
        if not isinstance(data, dict):
            return False
        
        if "structured_regulation" not in data:
            self.logger.error("Missing structured_regulation in input data")
            return False
        
        return True