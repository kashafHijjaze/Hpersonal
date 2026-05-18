import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    SITE_URL = os.getenv("SITE_URL", "http://localhost:5000")
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")
    HUGGINGFACE_IMAGE_MODEL = os.getenv(
        "HUGGINGFACE_IMAGE_MODEL", "stabilityai/stable-diffusion-xl-base-1.0"
    )
    LOCAL_DIFFUSION_MODEL = os.getenv("LOCAL_DIFFUSION_MODEL", "")
    REALESRGAN_MODEL_PATH = os.getenv("REALESRGAN_MODEL_PATH", "")
