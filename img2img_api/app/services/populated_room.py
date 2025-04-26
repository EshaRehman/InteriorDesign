import os
import time
import torch
import uuid
from PIL import Image
import logging
import asyncio
import json
from typing import Dict, Optional, Any, List, Tuple

from transformers import AutoProcessor, AutoModelForCausalLM
from controlnet_aux import CannyDetector
from ..core.logging import get_logger
from ..core.logging import get_logger
from ..utils.helpers import save_image, resize_image
from ...ml_models.model_manager import ModelManager
# from ..app.ml_models.model_manager import ModelManager
from openai import OpenAI

# Set up logger
logger = get_logger(__name__)


class PopulatedRoomService:
    """
    Service for populated room redesign using AI image generation models.
    """

    def __init__(self, model_manager: ModelManager = None):
        """
        Initialize the populated room service with required models.

        Args:
            model_manager: ModelManager instance to load and manage ML models
        """
        self.model_manager = model_manager or ModelManager()
        self.tasks = {}
        self.openai_client = None
        try:
            self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        except Exception as e:
            logger.warning(f"OpenAI client initialization failed: {e}. GPT prompt generation will be disabled.")

    def submit_redesign_task(self, input_image: Image.Image, request_id: str,
                             style: str, room_type: str, color_palette: Optional[str] = None) -> str:
        """
        Submit a redesign task to be processed asynchronously.

        Args:
            input_image: PIL Image object of the room to redesign
            request_id: Unique identifier for this request
            style: Design style to apply
            room_type: Type of room (bedroom, living room, etc.)
            color_palette: Optional color palette to use

        Returns:
            task_id: ID to check task status
        """
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            'status': 'pending',
            'request_id': request_id,
            'created_at': time.time()
        }

        # Start the async task
        asyncio.create_task(self._process_redesign(
            task_id=task_id,
            input_image=input_image,
            request_id=request_id,
            style=style,
            room_type=room_type,
            color_palette=color_palette
        ))

        return task_id

    async def _process_redesign(self, task_id: str, input_image: Image.Image, request_id: str,
                                style: str, room_type: str, color_palette: Optional[str] = None):
        """
        Process the redesign task asynchronously.

        Args:
            task_id: ID of the task
            input_image: PIL Image object of the room to redesign
            request_id: Unique identifier for this request
            style: Design style to apply
            room_type: Type of room
            color_palette: Optional color palette to use
        """
        self.tasks[task_id]['status'] = 'processing'

        try:
            # 1. Resize the input image if needed
            resized_image = resize_image(input_image, target_size=1400)

            # 2. Generate image description using Florence-2
            logger.info(f"Task {task_id}: Generating image description")
            description = self._generate_image_description(resized_image)

            # 3. Generate design prompts using GPT
            logger.info(f"Task {task_id}: Generating design prompts")
            prompts = self._generate_design_prompts(description, style, room_type, color_palette)

            # 4. Create Canny edge image
            logger.info(f"Task {task_id}: Creating control image")
            control_image = self._create_control_image(resized_image)

            # 5. Generate redesigned image
            logger.info(f"Task {task_id}: Generating redesigned image")
            output_image = self._generate_redesigned_image(
                control_image=control_image,
                clip_prompt=prompts["clip"],
                t5_prompt=prompts["t5"]
            )

            # 6. Save the output image
            output_path = save_image(output_image, f"outputs/{request_id}_output.png")

            # 7. Update task status
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['output_path'] = output_path
            self.tasks[task_id]['completed_at'] = time.time()

            logger.info(f"Task {task_id}: Redesign completed successfully")

        except Exception as e:
            logger.error(f"Task {task_id}: Error during redesign: {str(e)}")
            self.tasks[task_id]['status'] = 'failed'
            self.tasks[task_id]['error'] = str(e)

    def _generate_image_description(self, image: Image.Image) -> str:
        """
        Generate a detailed description of the input image using Florence-2 model.

        Args:
            image: PIL Image to describe

        Returns:
            str: Detailed description of the image
        """
        try:
            # Load Florence-2 model and processor
            florence_model = self.model_manager.get_model("florence-2")
            florence_processor = self.model_manager.get_processor("florence-2")

            device = florence_model.device
            torch_dtype = florence_model.dtype

            # Process the image
            inputs = florence_processor(
                text="<MORE_DETAILED_CAPTION>",
                images=image,
                return_tensors="pt"
            ).to(device, torch_dtype)

            # Generate description
            generated_ids = florence_model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=1024,
                do_sample=False,
                num_beams=3,
            )

            generated_text = florence_processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
            parsed_answer = florence_processor.post_process_generation(
                generated_text,
                task="<MORE_DETAILED_CAPTION>",
                image_size=(image.width, image.height)
            )

            return parsed_answer

        except Exception as e:
            logger.error(f"Error generating image description: {str(e)}")
            # Return a default description if Florence fails
            return "A room with furniture and decorations."

    def _generate_design_prompts(self, description: str, style: str,
                                 room_type: str, color_palette: Optional[str] = None) -> Dict[str, str]:
        """
        Generate design prompts using GPT based on the image description, style and color palette.

        Args:
            description: Image description from Florence
            style: Design style to apply
            room_type: Type of room
            color_palette: Optional color palette

        Returns:
            Dict with "clip" and "t5" prompts
        """
        # Default prompts in case GPT isn't available
        default_prompts = {
            "clip": f"A {style} {room_type} with elegant furniture, balanced lighting, and harmonious colors.",
            "t5": f"Transform this {room_type} into a {style} style space. Include furniture appropriate for a {room_type}, with balanced composition, proper lighting, and a cohesive color scheme that matches the {style} aesthetic."
        }

        if not self.openai_client:
            logger.warning("OpenAI client not available, using default prompts")
            return default_prompts

        try:
            # Add color instruction if provided
            color_instruction = f"and incorporate the specific color '{color_palette}' as a dominant theme throughout the entire room" if color_palette else "and use colors that are appropriate for the specified style"

            system_instruction = f"""
You are an 'Image Prompt Generator' for Flux image synthesis. Your task is to create two prompts—one for CLIP and one for T5—that clearly and powerfully integrate a {style} interior design style for a {room_type} while preserving the original room structure. The style must exert a strong and obvious influence in the resulting image, affecting materials, colors, and decor—but **not the room's architectural geometry**. {color_instruction}.

### Structural Constraint:
Do not modify fixed architectural elements such as:
- Window and door shapes (e.g., do not turn square windows into arches)
- Wall layout or dimensions
- Ceiling height or room footprint

You may vary:
- Surface finishes (e.g., wall materials, floor texture)
- Fabric, furniture, and color palette
- Patterns on rugs, chairs, and all interior items
- Lighting mood and fixtures
- Decorative objects

1. **CLIP Prompt:**  
   - Produce a concise, structured description of the room's key visual features.  
   - The prompt must be approximately 77 tokens (about 40-50 words).  
   - Focus solely on **core visual features** (layout, materials, lighting, furniture) that define the room's appearance in the context of the style.

2. **T5 Prompt:**  
   - Generate a detailed, technical description explicitly designed to guide the image generation model.  
   - The T5 prompt must be approximately 512 tokens (roughly 350-400 words) and follow a structured "recipe" format rather than a flowing narrative.  
   - Your description must include:
      - **Main Subject with Emphasis**: Use bracketed phrases to denote stylistically critical elements. For example:
       `[Low-profile tatami bed flanked by shoji screens and rice paper lamps]`
     - **Environmental & Lighting Dynamics**: Describe how light interacts with key materials and surfaces (e.g., `[sunlight filtering through slatted wooden blinds casts warm stripes on concrete floor]`).
     - **Perspective & Imaging Notes**: Specify depth-of-field, camera angle, lighting intensity, texture fidelity, etc.
   - Avoid speculative, narrative, or user-viewpoint language ("as if you see..." or "it feels like..."). Write in direct, **scene-construction language** suitable for image synthesis.

Always ensure that the visual output will reflect the **given style prominently** and not default to generic modern interiors.

Return your output as a JSON object with keys "clip" and "t5".
"""

            # Make the API call
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Description: {description}\nStyle: {style}\nRoom Type: {room_type}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )

            # Parse the response
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except (json.JSONDecodeError, AttributeError, IndexError) as e:
                logger.error(f"Error parsing GPT response: {str(e)}")
                return default_prompts

        except Exception as e:
            logger.error(f"Error generating design prompts with GPT: {str(e)}")
            return default_prompts

    def _create_control_image(self, image: Image.Image) -> Image.Image:
        """
        Create a control image using Canny edge detection.

        Args:
            image: Input image to process

        Returns:
            Processed control image
        """
        processor = CannyDetector()
        control_image = processor(
            image,
            low_threshold=50,
            high_threshold=100,
            detect_resolution=1024,
            image_resolution=1024
        )
        return control_image

    def _generate_redesigned_image(self, control_image: Image.Image,
                                   clip_prompt: str, t5_prompt: str) -> Image.Image:
        """
        Generate a redesigned image using the Flux pipeline.

        Args:
            control_image: Control image (Canny edges)
            clip_prompt: CLIP prompt for primary guidance
            t5_prompt: T5 prompt for detailed guidance

        Returns:
            Redesigned image
        """
        # Get the Flux pipeline
        pipe = self.model_manager.get_pipeline("flux-canny")

        # Generate the image
        result = pipe(
            prompt=clip_prompt,
            prompt_2=t5_prompt,
            control_image=control_image,
            height=1024,
            width=1024,
            num_inference_steps=50,
            guidance_scale=30.0,
            max_sequence_length=512
        )

        # Return the first image from the batch
        return result.images[0]

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task by ID.

        Args:
            task_id: ID of the task to check

        Returns:
            Dict with task status information
        """
        if task_id not in self.tasks:
            return {'status': 'not_found'}

        return self.tasks[task_id]