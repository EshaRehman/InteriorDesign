from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from img2img_api.app.core.logging import get_logger
# from .app.core.logging import get_logger

logger = get_logger(__name__)


class ImageProcessingError(Exception):
    """Exception raised for errors during image processing."""

    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class ModelLoadingError(Exception):
    """Exception raised when a model fails to load."""

    def __init__(self, detail: str, model_name: str):
        self.detail = detail
        self.model_name = model_name
        super().__init__(f"Error loading model {model_name}: {detail}")


def setup_exception_handlers(app):
    """
    Configure exception handlers for the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(ImageProcessingError)
    async def image_processing_exception_handler(request: Request, exc: ImageProcessingError):
        logger.error(f"Image processing error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(ModelLoadingError)
    async def model_loading_exception_handler(request: Request, exc: ModelLoadingError):
        logger.error(f"Model loading error: {exc.detail}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Failed to load model {exc.model_name}: {exc.detail}"}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Create a more user-friendly validation error message
        errors = exc.errors()
        error_messages = []

        for error in errors:
            field = ".".join(str(loc) for loc in error["loc"][1:]) if len(error["loc"]) > 1 else "Input"
            message = error["msg"]
            error_messages.append(f"{field}: {message}")

        logger.warning(f"Validation error: {', '.join(error_messages)}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": error_messages}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred. Please try again later."}
        )