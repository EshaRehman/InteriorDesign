from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import Form


class PopulatedRoomRequest(BaseModel):
    """
    Request model for populated room redesign
    """
    style: str = Form(..., description="Design style to apply (e.g., 'modern', 'minimalist', 'industrial')")
    room_type: str = Form(..., description="Type of room (e.g., 'bedroom', 'living room', 'kitchen')")
    color_palette: Optional[str] = Form(None, description="Optional color palette to use")

    class Config:
        schema_extra = {
            "example": {
                "style": "modern",
                "room_type": "living room",
                "color_palette": "Soft white, cool gray, walnut brown, with pops of navy blue"
            }
        }


class EmptyRoomRequest(BaseModel):
    """
    Request model for empty room redesign
    """
    style: str = Form(..., description="Design style to apply (e.g., 'modern', 'minimalist', 'industrial')")
    room_type: str = Form(..., description="Type of room to create (e.g., 'bedroom', 'living room', 'kitchen')")
    furniture: Optional[List[str]] = Form(None, description="Optional list of furniture items to include")
    color_palette: Optional[str] = Form(None, description="Optional color palette to use")

    class Config:
        schema_extra = {
            "example": {
                "style": "modern",
                "room_type": "living room",
                "furniture": ["sofa", "coffee table", "TV stand", "rug"],
                "color_palette": "Gray, white, with accent colors in teal and orange"
            }
        }


class InpaintingRequest(BaseModel):
    """
    Request model for image inpainting
    """
    prompt: str = Form(..., description="Text description of what to add or modify in the masked area")
    strength: float = Form(0.8, description="Strength of the inpainting effect (0.0 to 1.0)")

    class Config:
        schema_extra = {
            "example": {
                "prompt": "A modern gray sofa with decorative pillows",
                "strength": 0.8
            }
        }