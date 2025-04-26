from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import torch
import os
import time
import logging
from PIL import Image
import io
import uuid
from typing import Optional

from ...models.request_models import PopulatedRoomRequest
from ...models.response_models import ImageResponse
from ...services.populated_room import PopulatedRoomService
from ...core.logging import get_logger
from ...utils.helpers import save_image, get_image_url
from ...utils.validators import validate_image

router = APIRouter()
logger = get_logger(__name__)

# Add this function to create a proper dependency
def get_populated_room_service():
    return PopulatedRoomService()

@router.post("/", response_model=ImageResponse)
async def redesign_populated_room(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        data: PopulatedRoomRequest = Depends(),
        service: PopulatedRoomService = Depends(get_populated_room_service)  # Use the function here
):
    """
    Redesign a populated room by applying a specific style and color palette.

    The endpoint uses a multi-step process:
    1. Process the input image and validate
    2. Generate image description using Florence-2
    3. Create design prompts with GPT based on the description, style, and color
    4. Process image through Canny edge detector
    5. Generate the redesigned image using Flux pipeline

    Parameters:
    - file: The input image file of the room to redesign
    - data: Style, room type, and color palette parameters

    Returns:
    - An ImageResponse with the URL to the generated image
    """
    start_time = time.time()
    logger.info(f"Received populated room redesign request with style: {data.style}, room_type: {data.room_type}")

    try:
        # Validate and process the image
        image_content = await file.read()
        input_image = Image.open(io.BytesIO(image_content))

        # Validate image dimensions, size, etc.
        validate_image(input_image)

        # Generate a unique ID for this request
        request_id = str(uuid.uuid4())

        # Save the input image
        input_path = save_image(input_image, f"inputs/{request_id}_input.png")
        logger.info(f"Input image saved at {input_path}")

        # Process the redesign in the background to avoid timeout
        task_id = service.submit_redesign_task(
            input_image=input_image,
            request_id=request_id,
            style=data.style,
            room_type=data.room_type,
            color_palette=data.color_palette
        )

        # Return a response with the task ID
        processing_time = time.time() - start_time
        logger.info(f"Request processed in {processing_time:.2f} seconds")

        # Return the task ID for status checking and the eventual URL where the image will be available
        return ImageResponse(
            message="Room redesign processing started",
            output_url=get_image_url(f"{request_id}_output.png"),
            task_id=task_id,
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"Error processing redesign request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing redesign request: {str(e)}")