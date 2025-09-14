#!/usr/bin/env python3
"""
Simple demo showing the Chain of Extraction data models and configuration.
This demo doesn't require external dependencies like PyMuPDF or OpenAI.
"""

import sys
import json
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, '../src')
sys.path.insert(0, '.')


def demo_configuration():
    """Demonstrate configuration management."""
    print("=== Configuration Demo ===")
    
    from chain_of_extraction.models.document_models import PipelineConfig
    from chain_of_extraction.config.settings import get_settings
    
    # Create different pipeline configurations
    basic_config = PipelineConfig()
    print(f"✓ Basic config: OCR={basic_config.enable_ocr}, Extract={basic_config.enable_extraction}")
    
    advanced_config = PipelineConfig(
        enable_translation=True,
        target_languages=["en", "es", "fr", "de"],
        chunk_size=8000
    )
    print(f"✓ Advanced config: Translation={advanced_config.enable_translation}")
    print(f"  Languages: {advanced_config.target_languages}")
    
    # Save and load configuration
    config_file = Path("demo_config.json")
    with open(config_file, 'w') as f:
        json.dump(advanced_config.model_dump(), f, indent=2)
    print(f"✓ Config saved to {config_file}")
    
    # Load settings
    settings = get_settings()
    print(f"✓ Settings: model={settings.openai_model}, chunk_size={settings.chunk_size}")


def demo_data_models():
    """Demonstrate the data models used in the pipeline."""
    print("\n=== Data Models Demo ===")
    
    from chain_of_extraction.models.document_models import (
        ExtractedRegulation, DocumentType, OCRResult, ProcessingResult, 
        ExtractionStatus, TranslationResult
    )
    
    # Create a sample regulation
    regulation = ExtractedRegulation(
        title="EU Cosmetic Products Regulation",
        regulation_number="Regulation (EC) No 1223/2009",
        effective_date="July 11, 2013",
        issuing_authority="European Parliament and Council",
        prohibited_ingredients=[
            "Lead and its compounds",
            "Mercury and its compounds (except as preservatives)",
            "Hexachlorophene",
            "Asbestos"
        ],
        restricted_ingredients=[
            {
                "ingredient": "Methylparaben", 
                "restriction": "Maximum 0.4% (as acid)"
            },
            {
                "ingredient": "Propylparaben",
                "restriction": "Maximum 0.14% (as acid)"
            },
            {
                "ingredient": "Formaldehyde",
                "restriction": "Maximum 0.2% (as preservative only)"
            }
        ],
        permitted_ingredients=[
            "Aqua (Water)",
            "Glycerin",
            "Sodium Chloride",
            "Citric Acid"
        ],
        labeling_requirements=[
            "List of ingredients in descending order by weight",
            "Use of INCI (International Nomenclature of Cosmetic Ingredients)",
            "Declaration of allergenic substances above 0.001% (leave-on) or 0.01% (rinse-off)",
            "Best before date or period after opening (PAO)",
            "Precautions for use"
        ],
        testing_requirements=[
            "Cosmetic product safety assessment",
            "Product information file (PIF) maintenance",
            "Stability testing under normal storage conditions",
            "Microbiological testing if required"
        ],
        packaging_requirements=[
            "Information must be indelible and easily legible",
            "Language requirements as per national regulations",
            "Child-resistant packaging for specific products",
            "Packaging materials must not contaminate the product"
        ],
        penalties=[
            "Administrative sanctions up to 4% of annual turnover",
            "Product withdrawal from market",
            "Prohibition of marketing until compliance",
            "Criminal liability for serious health risks"
        ],
        exemptions=[
            "Small quantities for testing purposes",
            "Products manufactured for export outside EU",
            "One-off manufacture for specific customer"
        ],
        document_type=DocumentType.REGULATION,
        language="en",
        confidence_score=0.92
    )
    
    print(f"✓ Regulation created: {regulation.title}")
    print(f"  Number: {regulation.regulation_number}")
    print(f"  Authority: {regulation.issuing_authority}")
    print(f"  Prohibited ingredients: {len(regulation.prohibited_ingredients)}")
    print(f"  Restricted ingredients: {len(regulation.restricted_ingredients)}")
    print(f"  Labeling requirements: {len(regulation.labeling_requirements)}")
    print(f"  Confidence: {regulation.confidence_score}")
    
    # Create OCR result
    ocr_result = OCRResult(
        text="REGULATION (EC) No 1223/2009 OF THE EUROPEAN PARLIAMENT...",
        confidence=0.94,
        page_number=1,
        processing_time=1.8
    )
    print(f"✓ OCR result: {len(ocr_result.text)} chars, confidence={ocr_result.confidence}")
    
    # Create processing result
    processing_result = ProcessingResult(
        document_id="eu_cosmetic_reg_2009",
        file_path="/path/to/regulation.pdf",
        status=ExtractionStatus.COMPLETED,
        ocr_results=[ocr_result],
        extracted_regulation=regulation,
        processing_time=42.5
    )
    print(f"✓ Processing result: status={processing_result.status}, time={processing_result.processing_time}s")


def demo_json_output():
    """Demonstrate JSON output structure."""
    print("\n=== JSON Output Demo ===")
    
    from chain_of_extraction.models.document_models import (
        ExtractedRegulation, DocumentType, ProcessingResult, ExtractionStatus
    )
    
    # Create sample data
    regulation = ExtractedRegulation(
        title="Sample Cosmetic Regulation",
        regulation_number="REG-2024-001",
        prohibited_ingredients=["Substance A", "Substance B"],
        document_type=DocumentType.REGULATION,
        confidence_score=0.88
    )
    
    result = ProcessingResult(
        document_id="sample_doc",
        file_path="sample.pdf",
        status=ExtractionStatus.COMPLETED,
        extracted_regulation=regulation,
        processing_time=30.2
    )
    
    # Convert to JSON
    json_output = result.model_dump()
    
    print("✓ JSON structure preview:")
    print(json.dumps({
        "document_id": json_output["document_id"],
        "status": json_output["status"], 
        "regulation_title": json_output["extracted_regulation"]["title"],
        "prohibited_count": len(json_output["extracted_regulation"]["prohibited_ingredients"]),
        "confidence": json_output["extracted_regulation"]["confidence_score"]
    }, indent=2))


def demo_pipeline_concepts():
    """Demonstrate pipeline concepts without external dependencies."""
    print("\n=== Pipeline Concepts Demo ===")
    
    from chain_of_extraction.pipeline.base import Pipeline
    from chain_of_extraction.models.document_models import PipelineConfig
    
    # Show different pipeline configurations
    configs = {
        "OCR Only": PipelineConfig(
            enable_ocr=True,
            enable_extraction=False,
            enable_structuring=False,
            enable_translation=False
        ),
        "Full Processing": PipelineConfig(
            enable_ocr=True,
            enable_extraction=True,
            enable_structuring=True,
            enable_translation=False
        ),
        "With Translation": PipelineConfig(
            enable_ocr=True,
            enable_extraction=True,
            enable_structuring=True,
            enable_translation=True,
            target_languages=["en", "es", "fr"]
        )
    }
    
    for name, config in configs.items():
        stages = []
        if config.enable_ocr:
            stages.append("OCR")
        if config.enable_extraction:
            stages.append("Extraction")
        if config.enable_structuring:
            stages.append("Structure")
        if config.enable_translation:
            stages.append("Translation")
        
        print(f"✓ {name}: {' -> '.join(stages)}")
        if config.enable_translation:
            print(f"  Languages: {config.target_languages}")


def main():
    """Run the demonstration."""
    print("Chain of Extraction - Core Functionality Demo")
    print("=" * 55)
    
    try:
        demo_configuration()
        demo_data_models() 
        demo_json_output()
        demo_pipeline_concepts()
        
        print("\n" + "=" * 55)
        print("✓ All demos completed successfully!")
        print("\nThis demonstrates the core data structures and configuration.")
        print("To run the full pipeline with PDF processing:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set OPENAI_API_KEY environment variable")
        print("3. Run: python -m src.chain_of_extraction.main extract your_file.pdf")
        
    except Exception as e:
        print(f"✗ Demo failed with error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)