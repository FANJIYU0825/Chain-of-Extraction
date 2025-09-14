"""Basic tests for the Chain of Extraction pipeline."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import json

from src.chain_of_extraction.models.document_models import (
    PipelineConfig, ExtractedRegulation, DocumentType, ExtractionStatus
)
from src.chain_of_extraction.pipeline.base import Pipeline, PipelineBuilder


def test_pipeline_config_creation():
    """Test creating pipeline configuration."""
    config = PipelineConfig()
    
    assert config.enable_ocr is True
    assert config.enable_extraction is True
    assert config.enable_structuring is True
    assert config.enable_translation is False
    assert config.target_languages == ["en"]


def test_extracted_regulation_model():
    """Test ExtractedRegulation model creation and validation."""
    regulation = ExtractedRegulation(
        title="Test Regulation",
        regulation_number="TEST-001",
        prohibited_ingredients=["Lead", "Mercury"],
        document_type=DocumentType.REGULATION,
        confidence_score=0.85
    )
    
    assert regulation.title == "Test Regulation"
    assert regulation.regulation_number == "TEST-001"
    assert len(regulation.prohibited_ingredients) == 2
    assert regulation.document_type == DocumentType.REGULATION
    assert regulation.confidence_score == 0.85


def test_pipeline_builder():
    """Test pipeline builder pattern."""
    config = PipelineConfig(
        enable_ocr=True,
        enable_extraction=True,
        enable_structuring=True,
        enable_translation=False
    )
    
    builder = PipelineBuilder().with_config(config)
    assert builder.config == config


def test_pipeline_creation():
    """Test basic pipeline creation."""
    config = PipelineConfig()
    pipeline = Pipeline(config)
    
    assert len(pipeline.stages) == 0
    assert pipeline.config == config


def test_pipeline_validation():
    """Test pipeline validation."""
    config = PipelineConfig()
    pipeline = Pipeline(config)
    
    # Empty pipeline should be invalid
    assert pipeline.validate_pipeline() is False
    
    # Mock stage
    mock_stage = Mock()
    mock_stage.name = "TestStage"
    pipeline.add_stage(mock_stage)
    
    # Pipeline with stages should be valid
    assert pipeline.validate_pipeline() is True


@pytest.fixture
def sample_pdf_path():
    """Create a temporary PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp.write(b'%PDF-1.4\nTest PDF content')
        return Path(tmp.name)


def test_config_file_operations():
    """Test configuration file operations."""
    config = PipelineConfig(
        enable_translation=True,
        target_languages=["en", "es", "fr"]
    )
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        json.dump(config.model_dump(), tmp, indent=2)
        config_file = Path(tmp.name)
    
    # Read back the config
    with open(config_file) as f:
        config_data = json.load(f)
    
    loaded_config = PipelineConfig(**config_data)
    assert loaded_config.enable_translation is True
    assert loaded_config.target_languages == ["en", "es", "fr"]
    
    # Cleanup
    config_file.unlink()


def test_extraction_status_enum():
    """Test extraction status enumeration."""
    assert ExtractionStatus.PENDING == "pending"
    assert ExtractionStatus.PROCESSING == "processing" 
    assert ExtractionStatus.COMPLETED == "completed"
    assert ExtractionStatus.FAILED == "failed"


def test_document_type_enum():
    """Test document type enumeration."""
    assert DocumentType.REGULATION == "regulation"
    assert DocumentType.GUIDELINE == "guideline"
    assert DocumentType.STANDARD == "standard"
    assert DocumentType.NOTIFICATION == "notification"
    assert DocumentType.UNKNOWN == "unknown"


if __name__ == "__main__":
    # Run basic tests
    test_pipeline_config_creation()
    test_extracted_regulation_model()
    test_pipeline_builder()
    test_pipeline_creation()
    test_pipeline_validation()
    test_config_file_operations()
    test_extraction_status_enum()
    test_document_type_enum()
    
    print("✓ All basic tests passed!")