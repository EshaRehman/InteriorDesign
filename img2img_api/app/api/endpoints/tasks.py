from fastapi import APIRouter, Depends, HTTPException
from ...services.populated_room import PopulatedRoomService  # Fixed import
from ...models.response_models import TaskStatusResponse
from ...core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Add this function to create a proper dependency
def get_populated_room_service():
    return PopulatedRoomService()

@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
        task_id: str,
        service: PopulatedRoomService = Depends(get_populated_room_service)  # Use the function here
):
    """
    Get the status of a task by its ID.

    Args:
        task_id: ID of the task to check

    Returns:
        Task status information
    """
    task_info = service.get_task_status(task_id)

    if task_info.get("status") == "not_found":
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found"
        )

    # Convert task info to response model format
    response = {
        "task_id": task_id,
        "status": task_info.get("status"),
        "created_at": task_info.get("created_at"),
    }

    # Add optional fields if available
    if "output_path" in task_info:
        response["output_url"] = task_info.get("output_url")

    if "completed_at" in task_info:
        response["completed_at"] = task_info.get("completed_at")

    if "error" in task_info:
        response["error"] = task_info.get("error")

    return TaskStatusResponse(**response)