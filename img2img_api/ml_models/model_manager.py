import os
import torch
from typing import Dict, Any, Optional
import logging
from transformers import AutoProcessor, AutoModelForCausalLM, T5TokenizerFast
from diffusers import FluxControlPipeline
from controlnet_aux import CannyDetector
from img2img_api.app.core.config import settings
from img2img_api.app.core.logging import get_logger

# Set up logger
logger = get_logger(__name__)


class ModelManager:
    """
    Manages loading, caching, and access to ML models used in the application.
    """

    def __init__(self):
        """Initialize the model manager."""
        self.models = {}
        self.processors = {}
        self.pipelines = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        logger.info(f"Using device: {self.device} with dtype: {self.torch_dtype}")

    def get_model(self, model_name: str) -> Any:
        """
        Get a model by name, loading it if not already loaded.

        Args:
            model_name: Name of the model to load

        Returns:
            The requested model
        """
        if model_name in self.models:
            return self.models[model_name]

        logger.info(f"Loading model: {model_name}")

        if model_name == "florence-2":
            model = self._load_florence_model()
            self.models[model_name] = model
            return model
        else:
            raise ValueError(f"Unknown model: {model_name}")

    def get_processor(self, processor_name: str) -> Any:
        """
        Get a processor by name, loading it if not already loaded.

        Args:
            processor_name: Name of the processor to load

        Returns:
            The requested processor
        """
        if processor_name in self.processors:
            return self.processors[processor_name]

        logger.info(f"Loading processor: {processor_name}")

        if processor_name == "florence-2":
            processor = AutoProcessor.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)
            self.processors[processor_name] = processor
            return processor
        elif processor_name == "canny":
            processor = CannyDetector()
            self.processors[processor_name] = processor
            return processor
        else:
            raise ValueError(f"Unknown processor: {processor_name}")

    def get_pipeline(self, pipeline_name: str) -> Any:
        """
        Get a pipeline by name, loading it if not already loaded.

        Args:
            pipeline_name: Name of the pipeline to load

        Returns:
            The requested pipeline
        """
        if pipeline_name in self.pipelines:
            return self.pipelines[pipeline_name]

        logger.info(f"Loading pipeline: {pipeline_name}")

        if pipeline_name == "flux-canny":
            pipeline = self._load_flux_pipeline()
            self.pipelines[pipeline_name] = pipeline
            return pipeline
        else:
            raise ValueError(f"Unknown pipeline: {pipeline_name}")

    def _load_florence_model(self) -> Any:
        """
        Load the Florence-2 image captioning model.

        Returns:
            Loaded Florence model
        """
        try:
            florence_model = AutoModelForCausalLM.from_pretrained(
                "microsoft/Florence-2-base",
                torch_dtype=self.torch_dtype,
                trust_remote_code=True
            ).to(self.device)
            return florence_model
        except Exception as e:
            logger.error(f"Error loading Florence-2 model: {str(e)}")
            raise

    def _load_flux_pipeline(self) -> Any:
        """
        Load the Flux image generation pipeline.

        Returns:
            Loaded Flux pipeline
        """
        try:
            pipe = FluxControlPipeline.from_pretrained(
                "black-forest-labs/FLUX.1-Canny-dev",
                torch_dtype=self.torch_dtype
            ).to(self.device)

            # Enable CPU offload to save GPU memory
            pipe.enable_model_cpu_offload()

            return pipe
        except Exception as e:
            logger.error(f"Error loading Flux pipeline: {str(e)}")
            raise

    def unload_model(self, model_name: str) -> None:
        """
        Unload a model from memory.

        Args:
            model_name: Name of the model to unload
        """
        if model_name in self.models:
            logger.info(f"Unloading model: {model_name}")
            del self.models[model_name]
            torch.cuda.empty_cache()

    def unload_pipeline(self, pipeline_name: str) -> None:
        """
        Unload a pipeline from memory.

        Args:
            pipeline_name: Name of the pipeline to unload
        """
        if pipeline_name in self.pipelines:
            logger.info(f"Unloading pipeline: {pipeline_name}")
            del self.pipelines[pipeline_name]
            torch.cuda.empty_cache()