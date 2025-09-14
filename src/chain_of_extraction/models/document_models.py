"""Data models for document processing and extraction results."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class DocumentType(str, Enum):
    """Types of cosmetic regulation documents."""
    REGULATION = "regulation"
    GUIDELINE = "guideline" 
    STANDARD = "standard"
    NOTIFICATION = "notification"
    UNKNOWN = "unknown"


class ExtractionStatus(str, Enum):
    """Status of document processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OCRResult(BaseModel):
    """Result from OCR processing."""
    text: str = Field(..., description="Extracted text from PDF")
    confidence: float = Field(..., description="OCR confidence score")
    page_number: int = Field(..., description="Page number in PDF")
    processing_time: float = Field(..., description="Processing time in seconds")


class ExtractedRegulation(BaseModel):
    """Structured information extracted from cosmetic regulation."""
    title: Optional[str] = Field(None, description="Regulation title")
    regulation_number: Optional[str] = Field(None, description="Official regulation number")
    effective_date: Optional[str] = Field(None, description="When regulation becomes effective")
    issuing_authority: Optional[str] = Field(None, description="Authority that issued the regulation")
    
    # Key regulatory content
    prohibited_ingredients: List[str] = Field(default_factory=list, description="List of prohibited ingredients")
    restricted_ingredients: List[Dict[str, Any]] = Field(default_factory=list, description="Ingredients with restrictions")
    permitted_ingredients: List[str] = Field(default_factory=list, description="Explicitly permitted ingredients")
    
    # Requirements and standards
    labeling_requirements: List[str] = Field(default_factory=list, description="Labeling requirements")
    testing_requirements: List[str] = Field(default_factory=list, description="Testing and safety requirements")
    packaging_requirements: List[str] = Field(default_factory=list, description="Packaging requirements")
    
    # Compliance information
    penalties: List[str] = Field(default_factory=list, description="Penalties for non-compliance")
    exemptions: List[str] = Field(default_factory=list, description="Exemptions or special cases")
    
    # Metadata
    document_type: DocumentType = Field(default=DocumentType.UNKNOWN, description="Type of document")
    language: str = Field(default="unknown", description="Document language")
    confidence_score: float = Field(default=0.0, description="Extraction confidence")


class TranslationResult(BaseModel):
    """Result from translation processing."""
    original_language: str = Field(..., description="Source language")
    target_language: str = Field(..., description="Target language")
    translated_regulation: ExtractedRegulation = Field(..., description="Translated regulation data")
    translation_confidence: float = Field(..., description="Translation quality confidence")


class ProcessingResult(BaseModel):
    """Complete processing result for a document."""
    document_id: str = Field(..., description="Unique document identifier")
    file_path: str = Field(..., description="Path to source PDF file")
    status: ExtractionStatus = Field(..., description="Processing status")
    
    # Processing results
    ocr_results: List[OCRResult] = Field(default_factory=list, description="OCR results for each page")
    extracted_regulation: Optional[ExtractedRegulation] = Field(None, description="Extracted regulation data")
    translations: List[TranslationResult] = Field(default_factory=list, description="Translation results")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")


class PipelineConfig(BaseModel):
    """Configuration for the extraction pipeline."""
    enable_ocr: bool = Field(default=True, description="Enable OCR processing")
    enable_extraction: bool = Field(default=True, description="Enable LLM extraction")
    enable_structuring: bool = Field(default=True, description="Enable data structuring")
    enable_translation: bool = Field(default=False, description="Enable translation")
    
    target_languages: List[str] = Field(default_factory=lambda: ["en"], description="Target languages for translation")
    chunk_size: int = Field(default=4000, description="Text chunk size for LLM processing")
    max_retries: int = Field(default=3, description="Maximum retries for failed operations")