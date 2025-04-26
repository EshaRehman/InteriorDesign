# Image-to-Image Generation API

This API provides endpoints for room redesign and image inpainting using AI models.

## Features

- Redesign populated rooms with selected room type, style, and color palette
- Redesign empty rooms with selected room type and style
- Image inpainting for improving images

## Project Structure

```
img2img_api/
│
├── main.py                      # Main application entry point
├── requirements.txt             # Project dependencies
├── .env.example                 # Environment variable template
├── README.md                    # Project documentation
├── Dockerfile                   # For containerization
│
├── app/                         # Application code
│   ├── api/                     # API routes
│   │   ├── endpoints/           # API endpoint modules
│   │   └── router.py            # API router configuration
│   ├── core/                    # Core application modules
│   ├── models/                  # Data models and schemas
│   ├── services/                # Business logic
│   └── utils/                   # Utility functions
│
├── ml_models/                   # Machine learning model management
│   ├── pipelines/               # Image generation pipelines
│   ├── processors/              # Model-specific processing
│   └── registry/                # Model registry
│
├── tests/                       # Test cases
│
└── data/                        # Data storage
    ├── models/                  # Downloaded models
    ├── inputs/                  # Input storage
    └── outputs/                 # Output storage
```

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

## API Endpoints

- `POST /api/v1/redesign/populated`: Redesign a populated room
- `POST /api/v1/redesign/empty`: Redesign an empty room
- `POST /api/v1/inpainting`: Improve an image through inpainting

## Development

- Run tests: `pytest`
- Run with debug: `python main.py --debug`

   