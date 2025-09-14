"""Main CLI interface for the Chain of Extraction pipeline."""

import typer
import asyncio
import json
import os
import logging
from pathlib import Path
from typing import List, Optional
from tqdm import tqdm

from .pipeline.base import PipelineBuilder
from .models.document_models import PipelineConfig, ExtractionStatus
from .config.settings import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = typer.Typer(help="Chain of Extraction - Automated pipeline for OCR and LLM-based extraction from cosmetic regulation PDFs")


@app.command()
def extract(
    input_path: Path = typer.Argument(..., help="Path to PDF file or directory of PDF files"),
    output_dir: Path = typer.Option("./output", "--output", "-o", help="Output directory"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    enable_ocr: bool = typer.Option(True, "--ocr/--no-ocr", help="Enable OCR processing"),
    enable_extraction: bool = typer.Option(True, "--extract/--no-extract", help="Enable LLM extraction"),
    enable_structuring: bool = typer.Option(True, "--structure/--no-structure", help="Enable data structuring"),
    enable_translation: bool = typer.Option(False, "--translate/--no-translate", help="Enable translation"),
    target_languages: List[str] = typer.Option(["en"], "--lang", help="Target languages for translation"),
    output_format: str = typer.Option("json", "--format", help="Output format (json, csv)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Extract information from PDF documents using OCR and LLMs."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input
    if not input_path.exists():
        typer.echo(f"Error: Input path {input_path} does not exist", err=True)
        raise typer.Exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure pipeline
    pipeline_config = PipelineConfig(
        enable_ocr=enable_ocr,
        enable_extraction=enable_extraction,
        enable_structuring=enable_structuring,
        enable_translation=enable_translation,
        target_languages=target_languages
    )
    
    # Load additional config from file if provided
    if config_file and config_file.exists():
        with open(config_file) as f:
            config_data = json.load(f)
            pipeline_config = PipelineConfig(**config_data)
    
    # Build pipeline
    builder = PipelineBuilder().with_config(pipeline_config)
    
    if enable_ocr:
        builder.add_ocr_stage()
    if enable_extraction:
        builder.add_extraction_stage()
    if enable_structuring:
        builder.add_structure_stage()
    if enable_translation:
        builder.add_translation_stage()
    
    pipeline = builder.build()
    
    if not pipeline.validate_pipeline():
        typer.echo("Error: Invalid pipeline configuration", err=True)
        raise typer.Exit(1)
    
    # Get PDF files to process
    pdf_files = []
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        pdf_files.append(input_path)
    elif input_path.is_dir():
        pdf_files.extend(input_path.rglob("*.pdf"))
    else:
        typer.echo("Error: Input must be a PDF file or directory containing PDF files", err=True)
        raise typer.Exit(1)
    
    if not pdf_files:
        typer.echo("No PDF files found to process", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"Found {len(pdf_files)} PDF file(s) to process")
    typer.echo(f"Pipeline stages: {' -> '.join(pipeline.get_stage_names())}")
    
    # Process files
    asyncio.run(process_files(pdf_files, pipeline, output_dir, output_format))


async def process_files(pdf_files: List[Path], pipeline, output_dir: Path, output_format: str):
    """Process multiple PDF files through the pipeline."""
    results = []
    
    with tqdm(total=len(pdf_files), desc="Processing PDFs") as pbar:
        for pdf_file in pdf_files:
            pbar.set_description(f"Processing {pdf_file.name}")
            
            try:
                # Process through pipeline
                result = await pipeline.process(str(pdf_file), pdf_file.stem)
                results.append(result)
                
                # Save individual result
                output_file = output_dir / f"{pdf_file.stem}_result.{output_format}"
                save_result(result, output_file, output_format)
                
                status = "✓" if result.status == ExtractionStatus.COMPLETED else "✗"
                pbar.set_postfix_str(f"{status} {result.status.value}")
                
            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {e}")
                pbar.set_postfix_str(f"✗ failed")
            
            pbar.update(1)
    
    # Save combined results
    combined_file = output_dir / f"combined_results.{output_format}"
    save_combined_results(results, combined_file, output_format)
    
    # Print summary
    successful = sum(1 for r in results if r.status == ExtractionStatus.COMPLETED)
    failed = len(results) - successful
    
    typer.echo(f"\nProcessing complete!")
    typer.echo(f"Successful: {successful}")
    typer.echo(f"Failed: {failed}")
    typer.echo(f"Results saved to: {output_dir}")


def save_result(result, output_file: Path, output_format: str):
    """Save processing result to file."""
    if output_format == "json":
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result.model_dump(), f, indent=2, default=str, ensure_ascii=False)
    
    elif output_format == "csv":
        import csv
        # Simple CSV export for basic regulation info
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if result.extracted_regulation:
                reg = result.extracted_regulation
                writer.writerow(['Field', 'Value'])
                writer.writerow(['Title', reg.title])
                writer.writerow(['Regulation Number', reg.regulation_number])
                writer.writerow(['Effective Date', reg.effective_date])
                writer.writerow(['Issuing Authority', reg.issuing_authority])
                writer.writerow(['Prohibited Ingredients', '; '.join(reg.prohibited_ingredients)])
                writer.writerow(['Permitted Ingredients', '; '.join(reg.permitted_ingredients)])


def save_combined_results(results: List, output_file: Path, output_format: str):
    """Save combined processing results to file."""
    if output_format == "json":
        combined_data = [result.model_dump() for result in results]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, default=str, ensure_ascii=False)


@app.command()
def validate_config(
    config_file: Path = typer.Argument(..., help="Configuration file to validate")
):
    """Validate pipeline configuration file."""
    try:
        with open(config_file) as f:
            config_data = json.load(f)
        
        config = PipelineConfig(**config_data)
        typer.echo("✓ Configuration file is valid")
        typer.echo(f"OCR: {'enabled' if config.enable_ocr else 'disabled'}")
        typer.echo(f"Extraction: {'enabled' if config.enable_extraction else 'disabled'}")
        typer.echo(f"Structuring: {'enabled' if config.enable_structuring else 'disabled'}")
        typer.echo(f"Translation: {'enabled' if config.enable_translation else 'disabled'}")
        
    except Exception as e:
        typer.echo(f"✗ Configuration validation failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def create_config(
    output_file: Path = typer.Option("pipeline_config.json", "--output", "-o", help="Output configuration file")
):
    """Create a sample configuration file."""
    sample_config = PipelineConfig()
    
    with open(output_file, 'w') as f:
        json.dump(sample_config.model_dump(), f, indent=2)
    
    typer.echo(f"✓ Sample configuration created: {output_file}")


def main():
    """Main entry point."""
    # Check for required environment variables
    settings = get_settings()
    
    if not settings.openai_api_key:
        typer.echo(
            "Warning: OPENAI_API_KEY environment variable not set. "
            "LLM extraction will not work without it.",
            err=True
        )
    
    app()


if __name__ == "__main__":
    main()