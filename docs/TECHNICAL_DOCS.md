# Chain of Extraction - Technical Documentation

## Architecture Overview

The Chain of Extraction pipeline follows a modular design with four main processing stages that can be enabled or disabled independently:

1. **OCR Stage**: Extracts text from PDF documents
2. **Extraction Stage**: Uses LLM to identify key regulatory information  
3. **Structure Stage**: Cleans and standardizes extracted data
4. **Translation Stage**: Translates content to multiple languages

## System Components

### Core Models (`models/document_models.py`)

#### `ExtractedRegulation`
The primary data structure containing extracted regulatory information:

```python
class ExtractedRegulation(BaseModel):
    title: Optional[str]
    regulation_number: Optional[str] 
    effective_date: Optional[str]
    issuing_authority: Optional[str]
    prohibited_ingredients: List[str]
    restricted_ingredients: List[Dict[str, Any]]
    permitted_ingredients: List[str]
    labeling_requirements: List[str]
    testing_requirements: List[str]
    packaging_requirements: List[str]
    penalties: List[str]
    exemptions: List[str]
    document_type: DocumentType
    language: str
    confidence_score: float
```

#### `ProcessingResult`
Complete result of pipeline processing:

```python
class ProcessingResult(BaseModel):
    document_id: str
    file_path: str
    status: ExtractionStatus
    ocr_results: List[OCRResult]
    extracted_regulation: Optional[ExtractedRegulation]
    translations: List[TranslationResult]
    created_at: datetime
    completed_at: Optional[datetime]
    processing_time: Optional[float]
    error_message: Optional[str]
```

### Pipeline Architecture (`pipeline/`)

#### Base Pipeline (`base.py`)
- `PipelineStage`: Abstract base class for all stages
- `Pipeline`: Main orchestrator that executes stages sequentially
- `PipelineBuilder`: Builder pattern for constructing pipelines

#### Processing Stages

**OCR Stage** (`ocr_stage.py`)
- Extracts text from PDF using PyMuPDF and Tesseract
- Handles both direct text extraction and OCR for scanned documents
- Image preprocessing for better OCR accuracy

**Extraction Stage** (`extraction_stage.py`)
- Uses LangChain and OpenAI for LLM-based information extraction
- Handles text chunking for large documents
- Structured JSON extraction with retry logic

**Structure Stage** (`structure_stage.py`)
- Data cleaning and validation
- Deduplication and normalization
- Confidence score calculation based on completeness

**Translation Stage** (`translation_stage.py`)
- Multi-language translation using LLM
- Preserves structure while translating content
- Configurable target languages

### Services (`services/`)

#### OCR Service (`ocr_service.py`)
- PDF text extraction using PyMuPDF
- Fallback OCR using Tesseract for scanned pages
- Image preprocessing and confidence scoring

#### LLM Service (`llm_service.py`)
- OpenAI integration via LangChain
- Prompt engineering for regulation extraction
- Translation capabilities

### Configuration (`config/settings.py`)
Environment-based configuration management:

```python
class Settings(BaseModel):
    openai_api_key: Optional[str]
    openai_model: str = "gpt-3.5-turbo"
    tesseract_cmd: Optional[str]
    ocr_languages: List[str] = ["eng"]
    chunk_size: int = 4000
    overlap_size: int = 200
    max_workers: int = 4
    output_format: str = "json"
    target_languages: List[str] = ["en"]
```

## Processing Flow

1. **Input Validation**: Check PDF file exists and is readable
2. **OCR Processing**: Extract text from each page
3. **Text Chunking**: Split large text into manageable chunks
4. **LLM Extraction**: Process chunks to extract structured information
5. **Data Structuring**: Clean, validate, and normalize extracted data
6. **Translation** (optional): Translate to target languages
7. **Output Generation**: Save results in specified format

## Error Handling

- **Stage-level**: Each stage handles its own errors and can skip processing
- **Pipeline-level**: Overall pipeline status tracking and error reporting
- **Retry Logic**: Configurable retry attempts for LLM API calls
- **Graceful Degradation**: Pipeline continues with partial results

## Performance Considerations

- **Chunked Processing**: Large documents split into smaller chunks
- **Parallel Processing**: Multiple workers for batch document processing  
- **Caching**: OCR results cached to avoid reprocessing
- **Memory Management**: Streaming for large files

## Extension Points

### Adding New Stages
1. Inherit from `PipelineStage`
2. Implement `process()` method
3. Add to `PipelineBuilder`

### Custom Data Models
1. Extend `ExtractedRegulation` for domain-specific fields
2. Update LLM prompts for new extraction targets
3. Modify output formatters

### New Output Formats
1. Add format handler in `main.py`
2. Implement serialization logic
3. Update CLI options

## Deployment Considerations

### Environment Variables
```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
OCR_LANGUAGES=eng,fra,deu,spa
CHUNK_SIZE=4000
MAX_WORKERS=4
```

### Dependencies
- **Core**: PyMuPDF, Tesseract, OpenAI, LangChain, Pydantic
- **Optional**: Additional Tesseract language packs
- **Development**: pytest for testing

### Scaling
- Horizontal scaling via multiple worker processes
- Queue-based processing for large document batches
- Cloud deployment with containerization

## Security Considerations

- API key management via environment variables
- Input validation for PDF files
- Sanitization of extracted text before processing
- No persistence of sensitive document content

## Testing Strategy

- **Unit Tests**: Individual component testing
- **Integration Tests**: Pipeline end-to-end testing
- **Mock Testing**: LLM and OCR service mocking
- **Configuration Tests**: Environment setup validation