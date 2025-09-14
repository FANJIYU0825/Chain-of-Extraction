"""Extraction stage for the extraction pipeline."""

from typing import Any, Dict
import logging
from .base import PipelineStage
from ..services.llm_service import LLMService
from ..models.document_models import PipelineConfig


logger = logging.getLogger(__name__)


class ExtractionStage(PipelineStage):
    """Pipeline stage for LLM-based information extraction."""
    
    def __init__(self, config: PipelineConfig):
        super().__init__("Extraction", config.__dict__)
        self.llm_service = LLMService()
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured information from text using LLM."""
        extracted_text = data.get("extracted_text", "")
        result = data["result"]
        
        if not extracted_text.strip():
            self.logger.warning("No text available for extraction")
            return data
        
        try:
            self.logger.info(f"Starting LLM extraction from {len(extracted_text)} characters")
            
            # Extract structured regulation information
            extracted_regulation = self.llm_service.extract_regulation_info(extracted_text)
            
            # Update result with extracted data
            result.extracted_regulation = extracted_regulation
            
            self.logger.info(f"Extraction completed. Found {len(extracted_regulation.prohibited_ingredients)} "
                           f"prohibited ingredients, {len(extracted_regulation.restricted_ingredients)} "
                           f"restricted ingredients")
            
            # Pass data to next stage
            data["extracted_regulation"] = extracted_regulation
            data["result"] = result
            
            return data
            
        except Exception as e:
            self.logger.error(f"LLM extraction failed: {e}")
            raise
    
    def validate_input(self, data: Any) -> bool:
        """Validate input has extracted text."""
        if not isinstance(data, dict):
            return False
        
        if "extracted_text" not in data:
            self.logger.error("Missing extracted_text in input data")
            return False
        
        return True