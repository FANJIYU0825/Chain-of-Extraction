"""LLM service for information extraction and processing."""

import openai
from typing import List, Dict, Any, Optional
import json
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from ..config.settings import get_settings
from ..models.document_models import ExtractedRegulation, DocumentType


logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based information extraction and processing."""
    
    def __init__(self):
        self.settings = get_settings()
        
        if not self.settings.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # Initialize LangChain ChatOpenAI
        self.llm = ChatOpenAI(
            api_key=self.settings.openai_api_key,
            model_name=self.settings.openai_model,
            temperature=0.1  # Low temperature for consistent extraction
        )
        
        # Initialize text splitter for handling long documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.overlap_size,
            separators=["\n\n", "\n", ".", "!", "?", ";", " ", ""]
        )
    
    def extract_regulation_info(self, text: str) -> ExtractedRegulation:
        """Extract structured regulation information from text."""
        try:
            self.logger.info(f"Starting regulation extraction from {len(text)} characters")
            
            # Split text into manageable chunks
            chunks = self.text_splitter.split_text(text)
            self.logger.info(f"Split text into {len(chunks)} chunks")
            
            # Process each chunk and combine results
            all_extractions = []
            for i, chunk in enumerate(chunks):
                self.logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                extraction = self._extract_from_chunk(chunk)
                if extraction:
                    all_extractions.append(extraction)
            
            # Combine all extractions
            combined = self._combine_extractions(all_extractions)
            
            self.logger.info("Regulation extraction completed successfully")
            return combined
            
        except Exception as e:
            self.logger.error(f"Regulation extraction failed: {e}")
            # Return empty structure on failure
            return ExtractedRegulation()
    
    def _extract_from_chunk(self, chunk: str) -> Optional[Dict[str, Any]]:
        """Extract information from a single text chunk."""
        system_prompt = """You are an expert at extracting key information from cosmetic regulation documents. 
        Extract structured information in JSON format. Focus on:
        
        1. Document metadata (title, regulation number, effective date, issuing authority)
        2. Prohibited ingredients (list of banned substances)
        3. Restricted ingredients (substances with limitations, including the restrictions)
        4. Permitted ingredients (explicitly allowed substances)
        5. Requirements (labeling, testing, packaging)
        6. Compliance information (penalties, exemptions)
        
        Return valid JSON with the following structure:
        {
            "title": "document title or null",
            "regulation_number": "official number or null",
            "effective_date": "date or null",
            "issuing_authority": "authority name or null",
            "prohibited_ingredients": ["ingredient1", "ingredient2"],
            "restricted_ingredients": [{"ingredient": "name", "restriction": "details"}],
            "permitted_ingredients": ["ingredient1", "ingredient2"],
            "labeling_requirements": ["requirement1", "requirement2"],
            "testing_requirements": ["requirement1", "requirement2"],
            "packaging_requirements": ["requirement1", "requirement2"],
            "penalties": ["penalty1", "penalty2"],
            "exemptions": ["exemption1", "exemption2"],
            "document_type": "regulation|guideline|standard|notification|unknown",
            "language": "language code"
        }
        
        If information is not present, use null or empty arrays as appropriate."""
        
        human_prompt = f"Extract structured information from this cosmetic regulation text:\n\n{chunk}"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:-3].strip()
            
            extraction_data = json.loads(response_text)
            return extraction_data
            
        except Exception as e:
            self.logger.warning(f"Failed to extract from chunk: {e}")
            return None
    
    def _combine_extractions(self, extractions: List[Dict[str, Any]]) -> ExtractedRegulation:
        """Combine multiple extraction results into a single structured result."""
        if not extractions:
            return ExtractedRegulation()
        
        combined = {
            "title": None,
            "regulation_number": None,
            "effective_date": None,
            "issuing_authority": None,
            "prohibited_ingredients": [],
            "restricted_ingredients": [],
            "permitted_ingredients": [],
            "labeling_requirements": [],
            "testing_requirements": [],
            "packaging_requirements": [],
            "penalties": [],
            "exemptions": [],
            "document_type": DocumentType.UNKNOWN,
            "language": "unknown",
            "confidence_score": 0.8  # Default confidence
        }
        
        # Combine all results
        for extraction in extractions:
            # Take first non-null value for single-value fields
            for field in ["title", "regulation_number", "effective_date", "issuing_authority"]:
                if combined[field] is None and extraction.get(field):
                    combined[field] = extraction[field]
            
            # Combine lists, removing duplicates
            for field in ["prohibited_ingredients", "permitted_ingredients", 
                         "labeling_requirements", "testing_requirements", 
                         "packaging_requirements", "penalties", "exemptions"]:
                if extraction.get(field):
                    existing = set(combined[field])
                    new_items = [item for item in extraction[field] if item not in existing]
                    combined[field].extend(new_items)
            
            # Handle restricted ingredients with more complex structure
            if extraction.get("restricted_ingredients"):
                existing_ingredients = {item.get("ingredient", "") for item in combined["restricted_ingredients"]}
                for item in extraction["restricted_ingredients"]:
                    if item.get("ingredient") not in existing_ingredients:
                        combined["restricted_ingredients"].append(item)
            
            # Take document type if not unknown
            if extraction.get("document_type") and extraction["document_type"] != "unknown":
                combined["document_type"] = extraction["document_type"]
            
            # Take language if not unknown
            if extraction.get("language") and extraction["language"] != "unknown":
                combined["language"] = extraction["language"]
        
        # Convert to Pydantic model
        return ExtractedRegulation(**combined)
    
    def translate_text(self, text: str, target_language: str, source_language: str = None) -> str:
        """Translate text to target language."""
        if not text.strip():
            return text
        
        source_lang_prompt = f" from {source_language}" if source_language else ""
        
        system_prompt = f"""You are a professional translator specializing in legal and regulatory documents. 
        Translate the following text{source_lang_prompt} to {target_language}. 
        Maintain the original meaning, technical terminology, and legal precision. 
        Do not add explanations or notes, just provide the translation."""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=text)
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            return text  # Return original text if translation fails