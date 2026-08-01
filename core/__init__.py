"""Cross-platform literature-review workflow installer core."""

from .config import APP_NAME, SKILLS, DOWNLOAD_URLS
from .detect import DetectionResult, detect_environment

__all__ = [
    "APP_NAME",
    "SKILLS",
    "DOWNLOAD_URLS",
    "DetectionResult",
    "detect_environment",
]
