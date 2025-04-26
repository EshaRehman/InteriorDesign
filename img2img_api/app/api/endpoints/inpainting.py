from fastapi import APIRouter

# Create stub router - will be implemented in the future
router = APIRouter()

@router.post("/")
async def inpaint_image():
    """
    Stub endpoint for image inpainting.
    This will be implemented in a future update.
    """
    return {"message": "This endpoint is not yet implemented"}