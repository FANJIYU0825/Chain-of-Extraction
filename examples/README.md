# Usage Examples

This directory contains examples of how to use the Chain of Extraction pipeline.

## Configuration Examples

### Basic Configuration
```json
{
  "enable_ocr": true,
  "enable_extraction": true,
  "enable_structuring": true,
  "enable_translation": false,
  "target_languages": ["en"],
  "chunk_size": 4000,
  "max_retries": 3
}
```

### Multi-language Configuration
```json
{
  "enable_ocr": true,
  "enable_extraction": true,
  "enable_structuring": true,
  "enable_translation": true,
  "target_languages": ["en", "es", "fr", "de"],
  "chunk_size": 6000,
  "max_retries": 5
}
```

## Command Line Usage Examples

### Process a Single PDF
```bash
# Basic extraction
python -m src.chain_of_extraction.main extract document.pdf

# With translation
python -m src.chain_of_extraction.main extract document.pdf --translate --lang en --lang es

# Custom output directory
python -m src.chain_of_extraction.main extract document.pdf --output ./results

# CSV output format
python -m src.chain_of_extraction.main extract document.pdf --format csv
```

### Process Multiple PDFs
```bash
# Process all PDFs in a directory
python -m src.chain_of_extraction.main extract /path/to/pdfs/ --output ./batch_results

# Process with custom configuration
python -m src.chain_of_extraction.main extract /path/to/pdfs/ --config my_config.json
```

## Programmatic Usage

### Basic Pipeline Usage
```python
import asyncio
from pathlib import Path
from chain_of_extraction.pipeline.base import PipelineBuilder
from chain_of_extraction.models.document_models import PipelineConfig

async def process_document():
    # Configure pipeline
    config = PipelineConfig(
        enable_ocr=True,
        enable_extraction=True,
        enable_structuring=True,
        enable_translation=False
    )
    
    # Build pipeline
    pipeline = (PipelineBuilder()
               .with_config(config)
               .add_ocr_stage()
               .add_extraction_stage()
               .add_structure_stage()
               .build())
    
    # Process document
    result = await pipeline.process("document.pdf")
    
    # Access results
    if result.extracted_regulation:
        regulation = result.extracted_regulation
        print(f"Title: {regulation.title}")
        print(f"Prohibited ingredients: {regulation.prohibited_ingredients}")
        print(f"Confidence: {regulation.confidence_score}")

# Run the pipeline
asyncio.run(process_document())
```

### Custom Stage Configuration
```python
from chain_of_extraction.models.document_models import PipelineConfig

# OCR-only pipeline
ocr_config = PipelineConfig(
    enable_ocr=True,
    enable_extraction=False,
    enable_structuring=False,
    enable_translation=False
)

# Translation-enabled pipeline
translation_config = PipelineConfig(
    enable_ocr=True,
    enable_extraction=True,
    enable_structuring=True,
    enable_translation=True,
    target_languages=["en", "es", "fr", "de", "it"]
)
```

## Expected Output Structure

### JSON Output Example
```json
{
  "document_id": "cosmetic_reg_001",
  "file_path": "/path/to/document.pdf",
  "status": "completed",
  "processing_time": 45.7,
  "ocr_results": [
    {
      "text": "COMMISSION REGULATION (EU) No 1223/2009...",
      "confidence": 0.95,
      "page_number": 1,
      "processing_time": 3.2
    }
  ],
  "extracted_regulation": {
    "title": "Commission Regulation (EU) No 1223/2009 on cosmetic products",
    "regulation_number": "EU 1223/2009",
    "effective_date": "July 11, 2013",
    "issuing_authority": "European Commission",
    "prohibited_ingredients": [
      "Lead and its compounds",
      "Mercury and its compounds",
      "Asbestos"
    ],
    "restricted_ingredients": [
      {
        "ingredient": "Parabens (Methylparaben, Ethylparaben)",
        "restriction": "Maximum concentration of 0.4% (as acid) for individual use or 0.8% for mixtures"
      }
    ],
    "permitted_ingredients": [
      "Water (Aqua)",
      "Glycerin",
      "Sodium chloride"
    ],
    "labeling_requirements": [
      "List of ingredients using INCI names",
      "Declaration of presence of allergens",
      "Best before date or period after opening"
    ],
    "testing_requirements": [
      "Safety assessment by qualified person",
      "Product information file maintenance",
      "Cosmetic product safety report"
    ],
    "packaging_requirements": [
      "Child-resistant packaging for certain products",
      "Information visible and legible",
      "Language requirements per member state"
    ],
    "penalties": [
      "Administrative fines up to 4% of annual turnover",
      "Product withdrawal from market",
      "Criminal prosecution for serious violations"
    ],
    "document_type": "regulation",
    "language": "en",
    "confidence_score": 0.89
  },
  "translations": []
}
```

## Environment Setup

### Required Environment Variables
```bash
# Copy from .env.example
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OCR_LANGUAGES=eng,fra,deu,spa
TARGET_LANGUAGES=en,es,fr
CHUNK_SIZE=4000
OUTPUT_DIR=./output
```

### Installation Commands
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .

# Install additional OCR languages (Ubuntu/Debian)
sudo apt-get install tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-spa
```