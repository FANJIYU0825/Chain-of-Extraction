"""OCR stage for the extraction pipeline."""

from typing import Any, Dict
import logging
from .base import PipelineStage
from ..services.ocr_service import OCRService
from ..models.document_models import PipelineConfig


logger = logging.getLogger(__name__)


class OCRStage(PipelineStage):
    """Pipeline stage for OCR text extraction from PDF documents."""
    
    def __init__(self, config: PipelineConfig):
        super().__init__("OCR", config.__dict__)
        self.ocr_service = OCRService()
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text from PDF using OCR."""
        file_path = data["file_path"]
        result = data["result"]
        
        try:
            self.logger.info(f"Starting OCR processing for {file_path}")
            
            # Extract text from PDF
            ocr_results = self.ocr_service.extract_text_from_pdf(file_path)
            
            # Update result with OCR data
            result.ocr_results = ocr_results
            
            # Combine all OCR text for next stages
            combined_text, avg_confidence = self.ocr_service.combine_ocr_results(ocr_results)
            
            self.logger.info(f"OCR completed. Extracted {len(combined_text)} characters "
                           f"with {avg_confidence:.2f} average confidence")
            
            # Pass extracted text to next stage
            data["extracted_text"] = combined_text
            data["ocr_confidence"] = avg_confidence
            data["result"] = result
            
            return data
            
        except Exception as e:
            self.logger.error(f"OCR processing failed: {e}")
            raise
    
    def validate_input(self, data: Any) -> bool:
        """Validate input has required file path."""
        if not isinstance(data, dict):
            return False
        
        if "file_path" not in data:
            self.logger.error("Missing file_path in input data")
            return False
        
        file_path = data["file_path"]
        if not isinstance(file_path, str) or not file_path.endswith('.pdf'):
            self.logger.error("file_path must be a PDF file")
            return False
        
        return True