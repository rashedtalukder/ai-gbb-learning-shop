"""
Validation utilities for Rashed's Sora SDK.
"""

from typing import Tuple, List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Supported video resolutions (width, height)
SUPPORTED_RESOLUTIONS = [
    (360, 360),  # 360x360p
    (640, 360),  # 640x360p
    (480, 480),  # 480x480p
    (854, 480),  # 854x480p
    (720, 720),  # 720x720p
    (1280, 720),  # 1280x720p
    (1080, 1080),  # 1080x1080p
    (1920, 1080)  # 1920x1080p
]

# Maximum duration in seconds for different resolution categories
MAX_DURATION = {
    'standard': 20,  # Standard resolution (up to 720p)
    'high': 10       # High resolution (1080p)
}

# Maximum number of variants for different resolution categories
MAX_VARIANTS = {
    'standard': 2,   # Standard resolution (up to 720p)
    'high': 1        # High resolution (1080p)
}

# Maximum number of pending tasks allowed
MAX_PENDING_TASKS = 1


class ValidationError(Exception):
    """Exception raised for validation errors in the Sora SDK."""
    pass


def validate_resolution(width: int, height: int) -> Tuple[int, int]:
    """
    Validate that the resolution is supported by the Sora API.

    Args:
        width: Video width in pixels
        height: Video height in pixels

    Returns:
        Tuple of validated (width, height)

    Raises:
        ValidationError: If the resolution is not supported
    """
    if (width, height) not in SUPPORTED_RESOLUTIONS:
        supported_str = ", ".join(
            [f"{w}x{h}" for w, h in SUPPORTED_RESOLUTIONS])
        raise ValidationError(
            f"Resolution {width}x{height} is not supported. Supported resolutions: {supported_str}"
        )

    return width, height


def validate_duration(width: int, height: int, duration: int) -> int:
    """
    Validate that the duration is within the allowed limits for the resolution.

    Args:
        width: Video width in pixels
        height: Video height in pixels
        duration: Video duration in seconds

    Returns:
        Validated duration in seconds

    Raises:
        ValidationError: If the duration exceeds the maximum allowed
    """
    # Determine if this is high resolution
    is_high_res = width >= 1080 or height >= 1080
    max_duration = MAX_DURATION['high'] if is_high_res else MAX_DURATION['standard']

    if duration > max_duration:
        raise ValidationError(
            f"Maximum duration for {width}x{height} is {max_duration} seconds. Got {duration} seconds."
        )

    if duration <= 0:
        raise ValidationError("Duration must be greater than 0 seconds.")

    return duration


def validate_variants(width: int, height: int, variants: int) -> int:
    """
    Validate that the number of variants is within the allowed limits for the resolution.

    Args:
        width: Video width in pixels
        height: Video height in pixels
        variants: Number of video variants to generate

    Returns:
        Validated number of variants

    Raises:
        ValidationError: If the number of variants exceeds the maximum allowed
    """
    # Determine if this is high resolution
    is_high_res = width >= 1080 or height >= 1080
    max_variants = MAX_VARIANTS['high'] if is_high_res else MAX_VARIANTS['standard']

    if variants > max_variants:
        raise ValidationError(
            f"Maximum variants for {width}x{height} is {max_variants}. Got {variants} variants."
        )

    if variants <= 0:
        raise ValidationError("Number of variants must be greater than 0.")

    return variants


def validate_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the complete video generation request.

    Args:
        request_data: Video generation request data

    Returns:
        Validated request data

    Raises:
        ValidationError: If any validation fails
    """
    # Extract parameters
    width = request_data.get('width')
    height = request_data.get('height')
    n_seconds = request_data.get('n_seconds')
    n_variants = request_data.get('n_variants', 1)

    # Validate individual parameters
    validate_resolution(width, height)
    validate_duration(width, height, n_seconds)
    validate_variants(width, height, n_variants)

    # Return the validated request
    return request_data
