import os
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings."""

    # API settings
    API_VERSION: str = "v1"
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    # Application settings
    APP_NAME: str = "Interior Design Image-to-Image API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Path settings
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    MODEL_DIR: str = os.path.join(BASE_DIR, "data", "models")

    # Input/output paths
    INPUT_DIR: str = os.path.join(DATA_DIR, "inputs")
    OUTPUT_DIR: str = os.path.join(DATA_DIR, "outputs")

    # Model settings
    HUGGINGFACE_TOKEN: Optional[str] = os.getenv("HUGGINGFACE_TOKEN")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Valid design styles
    VALID_STYLES: List[str] = [
        "modern", "minimalist", "industrial", "scandinavian",
        "bohemian", "farmhouse", "traditional", "contemporary",
        "mediterranean", "mid-century modern", "coastal", "gothic",
        "art deco", "japanese", "rustic", "transitional"
    ]

    # Valid room types
    VALID_ROOM_TYPES: List[str] = [
        "living room", "bedroom", "kitchen", "bathroom", "dining room",
        "office", "entryway", "hallway", "den", "nursery", "game room",
        "study", "sunroom", "basement", "loft", "attic"
    ]

    # Model constants
    DEFAULT_IMAGE_SIZE: int = 1024
    MAX_CLIP_TOKENS: int = 77
    MAX_T5_TOKENS: int = 512

    class Config:
        env_file = ".env"


# Create global settings object
settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.INPUT_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.MODEL_DIR, exist_ok=True)