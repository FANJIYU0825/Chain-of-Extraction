"""Structure stage for the extraction pipeline."""

from typing import Any, Dict
import logging
import json
from datetime import datetime
from .base import PipelineStage
from ..models.document_models import PipelineConfig, ExtractedRegulation


logger = logging.getLogger(__name__)


class StructureStage(PipelineStage):
    """Pipeline stage for structuring and validating extracted data."""
    
    def __init__(self, config: PipelineConfig):
        super().__init__("Structure", config.__dict__)
        self.config = config
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure and validate the extracted regulation data."""
        extracted_regulation = data.get("extracted_regulation")
        result = data["result"]
        
        if not extracted_regulation:
            self.logger.warning("No extracted regulation data to structure")
            return data
        
        try:
            self.logger.info("Starting data structuring and validation")
            
            # Validate and enhance the extracted data
            structured_regulation = self._structure_regulation(extracted_regulation)
            
            # Update result with structured data
            result.extracted_regulation = structured_regulation
            
            self.logger.info("Data structuring completed successfully")
            
            # Pass structured data to next stage
            data["structured_regulation"] = structured_regulation
            data["result"] = result
            
            return data
            
        except Exception as e:
            self.logger.error(f"Data structuring failed: {e}")
            raise
    
    def _structure_regulation(self, regulation: ExtractedRegulation) -> ExtractedRegulation:
        """Structure and validate regulation data."""
        # Clean and normalize text fields
        if regulation.title:
            regulation.title = self._clean_text(regulation.title)
        
        if regulation.regulation_number:
            regulation.regulation_number = self._clean_text(regulation.regulation_number)
        
        if regulation.issuing_authority:
            regulation.issuing_authority = self._clean_text(regulation.issuing_authority)
        
        # Clean and deduplicate ingredient lists
        regulation.prohibited_ingredients = self._clean_ingredient_list(
            regulation.prohibited_ingredients
        )
        regulation.permitted_ingredients = self._clean_ingredient_list(
            regulation.permitted_ingredients
        )
        
        # Clean restricted ingredients
        regulation.restricted_ingredients = self._clean_restricted_ingredients(
            regulation.restricted_ingredients
        )
        
        # Clean requirement lists
        regulation.labeling_requirements = self._clean_text_list(
            regulation.labeling_requirements
        )
        regulation.testing_requirements = self._clean_text_list(
            regulation.testing_requirements
        )
        regulation.packaging_requirements = self._clean_text_list(
            regulation.packaging_requirements
        )
        
        # Clean compliance information
        regulation.penalties = self._clean_text_list(regulation.penalties)
        regulation.exemptions = self._clean_text_list(regulation.exemptions)
        
        # Validate and enhance date format
        regulation.effective_date = self._normalize_date(regulation.effective_date)
        
        # Set confidence score based on data completeness
        regulation.confidence_score = self._calculate_confidence_score(regulation)
        
        return regulation
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return text
        
        # Remove extra whitespace and normalize
        cleaned = " ".join(text.strip().split())
        
        # Remove common OCR artifacts
        cleaned = cleaned.replace("  ", " ")
        cleaned = cleaned.replace(" .", ".")
        cleaned = cleaned.replace(" ,", ",")
        
        return cleaned
    
    def _clean_ingredient_list(self, ingredients: list) -> list:
        """Clean and deduplicate ingredient list."""
        if not ingredients:
            return []
        
        cleaned = []
        seen = set()
        
        for ingredient in ingredients:
            if isinstance(ingredient, str):
                clean_ingredient = self._clean_text(ingredient).lower()
                if clean_ingredient and clean_ingredient not in seen:
                    cleaned.append(ingredient.strip())
                    seen.add(clean_ingredient)
        
        return cleaned
    
    def _clean_restricted_ingredients(self, restricted: list) -> list:
        """Clean restricted ingredients data."""
        if not restricted:
            return []
        
        cleaned = []
        seen = set()
        
        for item in restricted:
            if isinstance(item, dict) and "ingredient" in item:
                ingredient = self._clean_text(item["ingredient"])
                restriction = self._clean_text(item.get("restriction", ""))
                
                ingredient_key = ingredient.lower()
                if ingredient and ingredient_key not in seen:
                    cleaned.append({
                        "ingredient": ingredient,
                        "restriction": restriction
                    })
                    seen.add(ingredient_key)
        
        return cleaned
    
    def _clean_text_list(self, text_list: list) -> list:
        """Clean and deduplicate text list."""
        if not text_list:
            return []
        
        cleaned = []
        seen = set()
        
        for text in text_list:
            if isinstance(text, str):
                clean_text = self._clean_text(text)
                text_key = clean_text.lower()
                if clean_text and text_key not in seen:
                    cleaned.append(clean_text)
                    seen.add(text_key)
        
        return cleaned
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date format."""
        if not date_str:
            return date_str
        
        # Simple date cleaning - could be enhanced with date parsing
        cleaned_date = self._clean_text(date_str)
        
        # Remove common date prefixes/suffixes
        cleaned_date = cleaned_date.replace("effective ", "")
        cleaned_date = cleaned_date.replace("date: ", "")
        
        return cleaned_date
    
    def _calculate_confidence_score(self, regulation: ExtractedRegulation) -> float:
        """Calculate confidence score based on data completeness."""
        score = 0.0
        max_score = 10.0
        
        # Basic information (40% of score)
        if regulation.title:
            score += 1.0
        if regulation.regulation_number:
            score += 1.0
        if regulation.effective_date:
            score += 1.0
        if regulation.issuing_authority:
            score += 1.0
        
        # Ingredient information (40% of score)
        if regulation.prohibited_ingredients:
            score += 1.5
        if regulation.restricted_ingredients:
            score += 1.5
        if regulation.permitted_ingredients:
            score += 1.0
        
        # Requirements and compliance (20% of score)
        if regulation.labeling_requirements:
            score += 0.5
        if regulation.testing_requirements:
            score += 0.5
        if regulation.packaging_requirements:
            score += 0.5
        if regulation.penalties or regulation.exemptions:
            score += 0.5
        
        return min(score / max_score, 1.0)
    
    def validate_input(self, data: Any) -> bool:
        """Validate input has extracted regulation."""
        if not isinstance(data, dict):
            return False
        
        if "extracted_regulation" not in data:
            self.logger.error("Missing extracted_regulation in input data")
            return False
        
        return True