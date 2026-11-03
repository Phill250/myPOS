"""Application settings, read once from environment variables.

Values come from the real environment first, then from a `.env` file in the
backend folder (if python-dotenv is installed). Nothing secret is hardcoded
here except a development-only fallback for the JWT key.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:  # dotenv is optional — plain env vars still work
    pass


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mypos_db"
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-secret-change-me-in-env-file")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Frontend origins allowed to call the API from a browser.
CORS_ORIGINS = _csv(
    os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
)

# Library rules (RWF)
LATE_FEE_PER_DAY = int(os.getenv("LATE_FEE_PER_DAY", "200"))
LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "3"))

# Kigali is UTC+2 all year (no daylight saving), so a fixed offset is enough
# and avoids needing the tzdata package on Windows.
UTC_OFFSET_HOURS = int(os.getenv("UTC_OFFSET_HOURS", "2"))
RECEIPT_PREFIX = os.getenv("RECEIPT_PREFIX", "CL")
