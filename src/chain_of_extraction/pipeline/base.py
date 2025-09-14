"""Base pipeline architecture for the Chain of Extraction workflow."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
from ..models.document_models import ProcessingResult, ExtractionStatus, PipelineConfig


logger = logging.getLogger(__name__)


class PipelineStage(ABC):
    """Abstract base class for pipeline stages."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def process(self, data: Any) -> Any:
        """Process data through this pipeline stage."""
        pass
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for this stage."""
        return True
    
    def handle_error(self, error: Exception, data: Any) -> Any:
        """Handle errors that occur during processing."""
        self.logger.error(f"Error in stage {self.name}: {error}")
        raise error


class Pipeline:
    """Main pipeline orchestrator for the extraction workflow."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.stages: List[PipelineStage] = []
        self.logger = logging.getLogger(__name__)
    
    def add_stage(self, stage: PipelineStage) -> "Pipeline":
        """Add a stage to the pipeline."""
        self.stages.append(stage)
        self.logger.info(f"Added stage: {stage.name}")
        return self
    
    async def process(self, file_path: str, document_id: str = None) -> ProcessingResult:
        """Process a document through the complete pipeline."""
        if document_id is None:
            document_id = f"doc_{int(datetime.utcnow().timestamp())}"
        
        result = ProcessingResult(
            document_id=document_id,
            file_path=file_path,
            status=ExtractionStatus.PROCESSING
        )
        
        try:
            self.logger.info(f"Starting pipeline processing for {file_path}")
            start_time = datetime.utcnow()
            
            # Initial data is just the file path
            current_data = {"file_path": file_path, "result": result}
            
            # Process through each stage
            for stage in self.stages:
                self.logger.info(f"Processing stage: {stage.name}")
                stage_start = datetime.utcnow()
                
                try:
                    if stage.validate_input(current_data):
                        current_data = await stage.process(current_data)
                    else:
                        raise ValueError(f"Invalid input for stage {stage.name}")
                    
                    stage_time = (datetime.utcnow() - stage_start).total_seconds()
                    self.logger.info(f"Stage {stage.name} completed in {stage_time:.2f}s")
                    
                except Exception as e:
                    result.status = ExtractionStatus.FAILED
                    result.error_message = f"Failed at stage {stage.name}: {str(e)}"
                    stage.handle_error(e, current_data)
                    return result
            
            # Update final result
            result.status = ExtractionStatus.COMPLETED
            result.completed_at = datetime.utcnow()
            result.processing_time = (result.completed_at - start_time).total_seconds()
            
            self.logger.info(f"Pipeline completed successfully in {result.processing_time:.2f}s")
            
        except Exception as e:
            result.status = ExtractionStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()
            self.logger.error(f"Pipeline failed: {e}")
        
        return result
    
    def get_stage_names(self) -> List[str]:
        """Get list of stage names in the pipeline."""
        return [stage.name for stage in self.stages]
    
    def validate_pipeline(self) -> bool:
        """Validate the complete pipeline configuration."""
        if not self.stages:
            self.logger.error("Pipeline has no stages configured")
            return False
        
        self.logger.info(f"Pipeline validated with {len(self.stages)} stages")
        return True


class PipelineBuilder:
    """Builder for constructing pipelines with different configurations."""
    
    def __init__(self):
        self.config = PipelineConfig()
        self._stages = []
    
    def with_config(self, config: PipelineConfig) -> "PipelineBuilder":
        """Set the pipeline configuration."""
        self.config = config
        return self
    
    def add_ocr_stage(self) -> "PipelineBuilder":
        """Add OCR stage to the pipeline."""
        if self.config.enable_ocr:
            self._stages.append("OCRStage")
        return self
    
    def add_extraction_stage(self) -> "PipelineBuilder":
        """Add extraction stage to the pipeline.""" 
        if self.config.enable_extraction:
            self._stages.append("ExtractionStage")
        return self
    
    def add_structure_stage(self) -> "PipelineBuilder":
        """Add structure stage to the pipeline."""
        if self.config.enable_structuring:
            self._stages.append("StructureStage")
        return self
    
    def add_translation_stage(self) -> "PipelineBuilder":
        """Add translation stage to the pipeline."""
        if self.config.enable_translation:
            self._stages.append("TranslationStage")
        return self
    
    def build(self) -> Pipeline:
        """Build and return the configured pipeline."""
        pipeline = Pipeline(self.config)
        
        for stage_name in self._stages:
            if stage_name == "OCRStage":
                from .ocr_stage import OCRStage
                stage = OCRStage(self.config)
            elif stage_name == "ExtractionStage":
                from .extraction_stage import ExtractionStage
                stage = ExtractionStage(self.config)
            elif stage_name == "StructureStage":
                from .structure_stage import StructureStage
                stage = StructureStage(self.config)
            elif stage_name == "TranslationStage":
                from .translation_stage import TranslationStage
                stage = TranslationStage(self.config)
            else:
                continue
            
            pipeline.add_stage(stage)
        
        return pipeline