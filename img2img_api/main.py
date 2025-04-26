import uvicorn
import argparse
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# from app.api.router import api_router
from img2img_api.app.api.router import api_router
from img2img_api.app.core.config import settings
from img2img_api.app.core.errors import setup_exception_handlers
from img2img_api.app.core.logging import get_logger
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="API for interior design image-to-image generation",
        version=settings.API_VERSION,
        debug=settings.DEBUG,
    )

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For production, specify the allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Set up exception handlers
    setup_exception_handlers(app)

    # Include API routes
    app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

    # Mount static files for output images
    app.mount("/data", StaticFiles(directory=settings.DATA_DIR), name="data")

    # Add a simple health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the API server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")

    args = parser.parse_args()

    logger.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(
   "img2img_api.main:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
    )