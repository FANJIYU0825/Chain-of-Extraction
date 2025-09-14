"""OCR service for extracting text from PDF documents."""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import List, Tuple
import logging
import tempfile
import os
from ..models.document_models import OCRResult
from ..config.settings import get_settings


logger = logging.getLogger(__name__)


class OCRService:
    """Service for optical character recognition on PDF documents."""
    
    def __init__(self):
        self.settings = get_settings()
        if self.settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.settings.tesseract_cmd
        
        # Configure OCR languages
        self.languages = "+".join(self.settings.ocr_languages)
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[OCRResult]:
        """Extract text from PDF using both direct text extraction and OCR."""
        results = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # First try direct text extraction
                direct_text = page.get_text()
                
                if direct_text.strip() and len(direct_text.strip()) > 50:
                    # If we get substantial text directly, use it
                    result = OCRResult(
                        text=direct_text,
                        confidence=1.0,  # Direct extraction has high confidence
                        page_number=page_num + 1,
                        processing_time=0.0
                    )
                    results.append(result)
                    logger.info(f"Extracted text directly from page {page_num + 1}")
                else:
                    # Fall back to OCR for scanned pages
                    ocr_result = self._ocr_page(page, page_num + 1)
                    results.append(ocr_result)
                    logger.info(f"Used OCR for page {page_num + 1}")
            
            doc.close()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            raise
        
        return results
    
    def _ocr_page(self, page: fitz.Page, page_number: int) -> OCRResult:
        """Perform OCR on a single PDF page."""
        import time
        start_time = time.time()
        
        try:
            # Render page as image
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR quality
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_file.write(img_data)
                tmp_file_path = tmp_file.name
            
            # Load and preprocess image
            image = cv2.imread(tmp_file_path)
            preprocessed = self._preprocess_image(image)
            
            # Perform OCR
            ocr_data = pytesseract.image_to_data(
                preprocessed, 
                lang=self.languages,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text and calculate confidence
            text_parts = []
            confidences = []
            
            for i, conf in enumerate(ocr_data['conf']):
                if int(conf) > 30:  # Filter low-confidence text
                    word = ocr_data['text'][i].strip()
                    if word:
                        text_parts.append(word)
                        confidences.append(int(conf))
            
            text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Cleanup
            os.unlink(tmp_file_path)
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                text=text,
                confidence=avg_confidence / 100.0,  # Convert to 0-1 scale
                page_number=page_number,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"OCR failed for page {page_number}: {e}")
            processing_time = time.time() - start_time
            
            return OCRResult(
                text="",
                confidence=0.0,
                page_number=page_number,
                processing_time=processing_time
            )
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def combine_ocr_results(self, results: List[OCRResult]) -> Tuple[str, float]:
        """Combine multiple OCR results into a single text and confidence score."""
        if not results:
            return "", 0.0
        
        combined_text = "\n\n".join([result.text for result in results if result.text.strip()])
        
        # Calculate weighted average confidence
        total_chars = sum(len(result.text) for result in results)
        if total_chars == 0:
            return "", 0.0
        
        weighted_confidence = sum(
            result.confidence * len(result.text) 
            for result in results
        ) / total_chars
        
        return combined_text, weighted_confidence