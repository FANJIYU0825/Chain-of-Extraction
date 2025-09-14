"""Configuration settings for the Chain of Extraction pipeline."""

import os
from typing import Optional, List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-3.5-turbo")
    
    # OCR Configuration
    tesseract_cmd: Optional[str] = Field(default=None)
    ocr_languages: List[str] = Field(default=["eng"])
    
    # Pipeline Configuration
    max_workers: int = Field(default=4)
    chunk_size: int = Field(default=4000)
    overlap_size: int = Field(default=200)
    
    # Output Configuration
    output_format: str = Field(default="json")  # json, csv, xml
    output_dir: str = Field(default="./output")
    
    # Translation Configuration
    target_languages: List[str] = Field(default=["en"])
    
    def __init__(self, **kwargs):
        # Load from environment variables
        env_values = {
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'openai_model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            'tesseract_cmd': os.getenv('TESSERACT_CMD'),
            'ocr_languages': os.getenv('OCR_LANGUAGES', 'eng').split(','),
            'max_workers': int(os.getenv('MAX_WORKERS', '4')),
            'chunk_size': int(os.getenv('CHUNK_SIZE', '4000')),
            'overlap_size': int(os.getenv('OVERLAP_SIZE', '200')),
            'output_format': os.getenv('OUTPUT_FORMAT', 'json'),
            'output_dir': os.getenv('OUTPUT_DIR', './output'),
            'target_languages': os.getenv('TARGET_LANGUAGES', 'en').split(','),
        }
        
        # Override with provided kwargs
        env_values.update(kwargs)
        
        super().__init__(**env_values)


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings