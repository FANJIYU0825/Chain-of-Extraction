#!/usr/bin/env python3
"""
Example script showing how to use the Chain of Extraction pipeline programmatically.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, '../src')

from chain_of_extraction.pipeline.base import PipelineBuilder
from chain_of_extraction.models.document_models import PipelineConfig, ExtractionStatus


async def basic_extraction_example():
    """Example of basic document extraction."""
    print("=== Basic Extraction Example ===")
    
    # Configure pipeline for basic extraction (no translation)
    config = PipelineConfig(
        enable_ocr=True,
        enable_extraction=True,
        enable_structuring=True,
        enable_translation=False,
        chunk_size=4000
    )
    
    # Build pipeline
    pipeline = (PipelineBuilder()
               .with_config(config)
               .add_ocr_stage()
               .add_extraction_stage()
               .add_structure_stage()
               .build())
    
    print(f"Pipeline stages: {' -> '.join(pipeline.get_stage_names())}")
    
    # Note: This would process a real PDF file
    # result = await pipeline.process("sample_regulation.pdf")
    
    print("✓ Pipeline configured successfully for basic extraction")


async def multilingual_extraction_example():
    """Example of multilingual document extraction."""
    print("\n=== Multilingual Extraction Example ===")
    
    # Configure pipeline with translation
    config = PipelineConfig(
        enable_ocr=True,
        enable_extraction=True,
        enable_structuring=True,
        enable_translation=True,
        target_languages=["en", "es", "fr"],
        chunk_size=6000
    )
    
    # Build pipeline
    pipeline = (PipelineBuilder()
               .with_config(config)
               .add_ocr_stage()
               .add_extraction_stage()
               .add_structure_stage()
               .add_translation_stage()
               .build())
    
    print(f"Pipeline stages: {' -> '.join(pipeline.get_stage_names())}")
    print(f"Target languages: {config.target_languages}")
    
    print("✓ Pipeline configured successfully for multilingual extraction")


async def ocr_only_example():
    """Example of OCR-only processing."""
    print("\n=== OCR-Only Example ===")
    
    # Configure pipeline for OCR only
    config = PipelineConfig(
        enable_ocr=True,
        enable_extraction=False,
        enable_structuring=False,
        enable_translation=False
    )
    
    # Build pipeline
    pipeline = (PipelineBuilder()
               .with_config(config)
               .add_ocr_stage()
               .build())
    
    print(f"Pipeline stages: {' -> '.join(pipeline.get_stage_names())}")
    print("✓ Pipeline configured successfully for OCR-only processing")


def demonstrate_models():
    """Demonstrate working with data models."""
    print("\n=== Data Models Example ===")
    
    from chain_of_extraction.models.document_models import (
        ExtractedRegulation, DocumentType, OCRResult
    )
    
    # Create sample regulation data
    regulation = ExtractedRegulation(
        title="Sample EU Cosmetic Regulation",
        regulation_number="EU-2024/001",
        effective_date="January 1, 2024",
        issuing_authority="European Commission",
        prohibited_ingredients=["Lead", "Mercury", "Asbestos"],
        restricted_ingredients=[
            {
                "ingredient": "Parabens",
                "restriction": "Maximum concentration 0.4%"
            },
            {
                "ingredient": "Formaldehyde",
                "restriction": "Prohibited except as preservative up to 0.2%"
            }
        ],
        permitted_ingredients=["Water", "Glycerin", "Sodium Chloride"],
        labeling_requirements=[
            "INCI names required",
            "Allergen declaration mandatory",
            "Best before date"
        ],
        testing_requirements=[
            "Safety assessment required",
            "Stability testing mandatory"
        ],
        document_type=DocumentType.REGULATION,
        language="en",
        confidence_score=0.92
    )
    
    print(f"Title: {regulation.title}")
    print(f"Regulation Number: {regulation.regulation_number}")
    print(f"Document Type: {regulation.document_type}")
    print(f"Prohibited Ingredients: {len(regulation.prohibited_ingredients)}")
    print(f"Restricted Ingredients: {len(regulation.restricted_ingredients)}")
    print(f"Confidence Score: {regulation.confidence_score}")
    
    # Create sample OCR result
    ocr_result = OCRResult(
        text="Commission Regulation (EU) No 1223/2009 on cosmetic products...",
        confidence=0.95,
        page_number=1,
        processing_time=2.3
    )
    
    print(f"OCR Text Length: {len(ocr_result.text)} characters")
    print(f"OCR Confidence: {ocr_result.confidence}")
    print(f"Processing Time: {ocr_result.processing_time}s")
    
    print("✓ Data models demonstrated successfully")


def demonstrate_configuration():
    """Demonstrate configuration management."""
    print("\n=== Configuration Example ===")
    
    from chain_of_extraction.config.settings import get_settings
    
    settings = get_settings()
    print(f"OpenAI Model: {settings.openai_model}")
    print(f"Chunk Size: {settings.chunk_size}")
    print(f"OCR Languages: {settings.ocr_languages}")
    print(f"Output Format: {settings.output_format}")
    
    print("✓ Configuration loaded successfully")


async def main():
    """Run all examples."""
    print("Chain of Extraction - Usage Examples")
    print("=" * 50)
    
    # Run async examples
    await basic_extraction_example()
    await multilingual_extraction_example()
    await ocr_only_example()
    
    # Run sync examples
    demonstrate_models()
    demonstrate_configuration()
    
    print("\n" + "=" * 50)
    print("✓ All examples completed successfully!")
    print("\nTo process real PDF files, ensure you have:")
    print("1. Set OPENAI_API_KEY environment variable")
    print("2. Installed all dependencies: pip install -r requirements.txt")
    print("3. A PDF file to process")
    print("\nExample command:")
    print("python -m src.chain_of_extraction.main extract your_document.pdf")


if __name__ == "__main__":
    asyncio.run(main())