from PIL import Image
from fastapi import HTTPException


def validate_image(image: Image.Image, min_size: int = 256, max_size: int = 4096,
                   max_file_size_mb: int = 10) -> None:
    """
    Validate if an image meets the requirements.

    Args:
        image: PIL Image to validate
        min_size: Minimum width or height in pixels
        max_size: Maximum width or height in pixels
        max_file_size_mb: Maximum file size in MB

    Raises:
        HTTPException: If the image doesn't meet requirements
    """
    # Check image dimensions
    width, height = image.size
    if width < min_size or height < min_size:
        raise HTTPException(
            status_code=400,
            detail=f"Image dimensions too small. Minimum size is {min_size}x{min_size} pixels."
        )

    if width > max_size or height > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"Image dimensions too large. Maximum size is {max_size}x{max_size} pixels."
        )

    # Check file format
    if image.format not in ["JPEG", "PNG", "JPG"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format. Please upload a JPEG or PNG image."
        )


def validate_color_palette(color_palette: str, max_length: int = 500) -> None:
    """
    Validate a color palette string.

    Args:
        color_palette: String describing a color palette
        max_length: Maximum character length

    Raises:
        HTTPException: If the color palette is invalid
    """
    if len(color_palette) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Color palette description too long. Maximum length is {max_length} characters."
        )


def validate_style(style: str, allowed_styles: list = None) -> None:
    """
    Validate if a style is allowed.

    Args:
        style: Style name to validate
        allowed_styles: List of allowed styles, if None all styles are allowed

    Raises:
        HTTPException: If the style is not allowed
    """
    if allowed_styles and style.lower() not in [s.lower() for s in allowed_styles]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid style. Allowed styles are: {', '.join(allowed_styles)}"
        )


def validate_room_type(room_type: str, allowed_room_types: list = None) -> None:
    """
    Validate if a room type is allowed.

    Args:
        room_type: Room type to validate
        allowed_room_types: List of allowed room types, if None all types are allowed

    Raises:
        HTTPException: If the room type is not allowed
    """
    if allowed_room_types and room_type.lower() not in [rt.lower() for rt in allowed_room_types]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid room type. Allowed room types are: {', '.join(allowed_room_types)}"
        )