from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ImageResponse(BaseModel):
    """
    Response model for image generation endpoints
    """
    message: str
    output_url: str
    task_id: Optional[str] = None
    processing_time: Optional[float] = None

    class Config:
        schema_extra = {
            "example": {
                "message": "Image generated successfully",
                "output_url": "https://example.com/data/outputs/abc123_output.png",
                "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "processing_time": 2.45
            }
        }


class TaskStatusResponse(BaseModel):
    """
    Response model for task status checking
    """
    task_id: str
    status: str
    output_url: Optional[str] = None
    error: Optional[str] = None
    created_at: float
    completed_at: Optional[float] = None

    class Config:
        schema_extra = {
            "example": {
                "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "status": "completed",
                "output_url": "https://example.com/data/outputs/abc123_output.png",
                "created_at": 1619683200.0,
                "completed_at": 1619683260.0
            }
        }


class ErrorResponse(BaseModel):
    """
    Response model for errors
    """
    detail: str

    class Config:
        schema_extra = {
            "example": {
                "detail": "Invalid image format. Please upload a JPEG or PNG image."
            }
        }