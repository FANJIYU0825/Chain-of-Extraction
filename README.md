# Chain-of-Extraction

This automated pipeline uses OCR and LLMs to extract, structure, and translate key information from unstructured or semi-structured cosmetic regulation documents in PDF format.

## 🚀 Features

- **Modular Design**: Multi-stage pipeline with configurable components
- **OCR Processing**: Extract text from scanned PDFs using advanced OCR techniques
- **LLM-Based Extraction**: Use Large Language Models to identify and structure key regulatory information
- **Data Structuring**: Standardize extracted information into consistent formats
- **Multi-language Translation**: Translate regulations to multiple target languages
- **Batch Processing**: Process multiple PDF documents efficiently
- **Flexible Output**: Support for JSON and CSV output formats

## 🏗️ Pipeline Architecture

The extraction workflow consists of four sequential stages:

1. **OCR Stage**: Extract text from PDF documents using PyMuPDF and Tesseract OCR
2. **Extraction Stage**: Use LLMs to identify key regulatory information (prohibited ingredients, requirements, etc.)
3. **Structure Stage**: Clean, validate, and standardize the extracted data
4. **Translation Stage**: Translate content to target languages (optional)

## 📋 Extracted Information

The pipeline extracts and structures the following types of information:

- Document metadata (title, regulation number, effective date, issuing authority)
- **Prohibited ingredients**: List of banned substances
- **Restricted ingredients**: Substances with usage limitations and restrictions
- **Permitted ingredients**: Explicitly allowed substances
- **Requirements**: Labeling, testing, and packaging requirements
- **Compliance information**: Penalties and exemptions

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key for LLM processing
- Tesseract OCR (optional, for enhanced OCR capabilities)

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/FANJIYU0825/Chain-of-Extraction.git
cd Chain-of-Extraction

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your configuration:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   OCR_LANGUAGES=eng,fra,deu,spa
   TARGET_LANGUAGES=en,es,fr
   ```

## 🚀 Quick Start

### Basic Usage

Extract information from a single PDF:
```bash
python -m chain_of_extraction.main extract document.pdf
```

Process multiple PDFs in a directory:
```bash
python -m chain_of_extraction.main extract /path/to/pdf/directory --output ./results
```

### Advanced Usage

Customize pipeline stages:
```bash
# Extract with translation enabled
python -m chain_of_extraction.main extract document.pdf --translate --lang en --lang es --lang fr

# OCR only (skip LLM processing)  
python -m chain_of_extraction.main extract document.pdf --no-extract --no-structure

# Custom output format
python -m chain_of_extraction.main extract document.pdf --format csv --output ./csv_results
```

### Configuration File

Create a configuration file for complex setups:
```bash
# Generate sample config
python -m chain_of_extraction.main create-config --output my_config.json

# Use custom config
python -m chain_of_extraction.main extract document.pdf --config my_config.json
```

## 📊 Output Format

### JSON Output Structure

```json
{
  "document_id": "doc_123456789",
  "file_path": "/path/to/document.pdf",
  "status": "completed",
  "extracted_regulation": {
    "title": "EU Cosmetic Regulation 1223/2009",
    "regulation_number": "EC 1223/2009",
    "effective_date": "July 11, 2013",
    "issuing_authority": "European Commission",
    "prohibited_ingredients": ["Lead", "Mercury", "Asbestos"],
    "restricted_ingredients": [
      {
        "ingredient": "Parabens",
        "restriction": "Maximum concentration 0.4%"
      }
    ],
    "permitted_ingredients": ["Water", "Glycerin"],
    "labeling_requirements": ["INCI names required", "Allergen declaration"],
    "testing_requirements": ["Safety assessment", "Stability testing"],
    "confidence_score": 0.85
  },
  "translations": [
    {
      "original_language": "en",
      "target_language": "es",
      "translated_regulation": { ... }
    }
  ]
}
```

## 🔧 Configuration Options

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| OpenAI API Key | `OPENAI_API_KEY` | - | Required for LLM processing |
| OpenAI Model | `OPENAI_MODEL` | `gpt-3.5-turbo` | LLM model to use |
| OCR Languages | `OCR_LANGUAGES` | `eng` | Tesseract OCR language codes |
| Chunk Size | `CHUNK_SIZE` | `4000` | Text chunk size for LLM processing |
| Max Workers | `MAX_WORKERS` | `4` | Parallel processing workers |
| Output Format | `OUTPUT_FORMAT` | `json` | Default output format |

## 🧪 Testing

Run basic functionality test:
```bash
# Create a sample config and validate
python -m chain_of_extraction.main create-config
python -m chain_of_extraction.main validate-config pipeline_config.json
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

**"OpenAI API key not set"**
- Set your API key in the `.env` file or `OPENAI_API_KEY` environment variable

**"Tesseract not found"**
- Install Tesseract OCR: `sudo apt-get install tesseract-ocr` (Ubuntu/Debian)
- Or set `TESSERACT_CMD` to the correct path

**"No PDF files found"**
- Ensure your input path contains valid PDF files
- Check file permissions

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation in the `docs/` directory
- Review example configurations in `examples/`
