import os
import time
from PIL import Image
from typing import Tuple, Optional
import uuid
from ..core.config import settings


def resize_image(input_img: Image.Image, target_size: int = 1400) -> Image.Image:
    """
    Resize an image while maintaining its aspect ratio.

    Args:
        input_img: The PIL Image to resize
        target_size: The maximum width or height of the resized image

    Returns:
        The resized PIL Image
    """
    # Get original dimensions
    width, height = input_img.size

    # If image is already smaller than target, return as is
    if width <= target_size and height <= target_size:
        return input_img

    # Compute the scaling factor
    scale_factor = target_size / max(width, height)

    # Compute new dimensions
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # Resize the image with aspect ratio preserved
    return input_img.resize((new_width, new_height), Image.LANCZOS)


def save_image(image: Image.Image, relative_path: str) -> str:
    """
    Save a PIL Image to the specified path.

    Args:
        image: The PIL Image to save
        relative_path: Path relative to the data directory

    Returns:
        The absolute path where the image was saved
    """
    # Ensure the directory exists
    full_path = os.path.join(settings.DATA_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # Save the image
    image.save(full_path)
    return full_path


def get_image_url(relative_path: str) -> str:
    """
    Generate a URL for an image based on its relative path.

    Args:
        relative_path: Path relative to the data directory

    Returns:
        URL for accessing the image
    """
    # Construct the URL based on the application's base URL
    return f"{settings.API_BASE_URL}/data/outputs/{os.path.basename(relative_path)}"


def generate_unique_id() -> str:
    """
    Generate a unique ID for file naming and request tracking.

    Returns:
        A unique string ID
    """
    return str(uuid.uuid4())


def format_processing_time(start_time: float) -> str:
    """
    Format processing time in a human-readable way.

    Args:
        start_time: Start time in seconds since epoch

    Returns:
        Formatted string of elapsed time
    """
    elapsed = time.time() - start_time
    if elapsed < 60:
        return f"{elapsed:.2f} seconds"
    elif elapsed < 3600:
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes} minutes {seconds} seconds"
    else:
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        return f"{hours} hours {minutes} minutes"