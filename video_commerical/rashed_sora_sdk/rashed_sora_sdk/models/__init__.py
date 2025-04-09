"""
Data models for the Azure OpenAI Sora Video Generation API.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union, Dict, Any
from datetime import datetime

from ..validation import (
    validate_resolution,
    validate_duration,
    validate_variants,
    validate_request,
    ValidationError
)


class JobStatus(str, Enum):
    """Status of a video generation job."""
    PREPROCESSING = "preprocessing"
    QUEUED = "queued"
    PROCESSING = "processing"
    RUNNING = "running"
    CANCELLED = "cancelled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class FailureReason(str, Enum):
    """Reason for job failure."""
    INPUT_MODERATION = "input_moderation"
    INTERNAL_ERROR = "internal_error"


@dataclass
class CreateVideoGenerationRequest:
    """Request parameters for creating a video generation job."""
    prompt: str
    height: int
    width: int
    n_seconds: int
    n_variants: int = 1

    def __post_init__(self):
        """Validate the request parameters after initialization."""
        try:
            # Validate individual fields
            validate_resolution(self.width, self.height)
            validate_duration(self.width, self.height, self.n_seconds)
            validate_variants(self.width, self.height, self.n_variants)
        except ValidationError as e:
            raise ValueError(f"Invalid request parameters: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        return {
            "prompt": self.prompt,
            "height": self.height,
            "width": self.width,
            "n_seconds": self.n_seconds,
            "n_variants": self.n_variants
        }


@dataclass
class VideoGeneration:
    """Details of a generated video."""
    id: str
    job_id: str
    created_at: int  # Unix timestamp
    width: int
    height: int
    n_seconds: int
    prompt: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoGeneration':
        """Create VideoGeneration from API response dictionary."""
        return cls(
            id=data["id"],
            job_id=data["job_id"],
            created_at=data["created_at"],
            width=data["width"],
            height=data["height"],
            n_seconds=data["n_seconds"],
            prompt=data["prompt"]
        )

    @property
    def created_datetime(self) -> datetime:
        """Convert Unix timestamp to datetime."""
        return datetime.fromtimestamp(self.created_at)


@dataclass
class VideoGenerationJob:
    """Details of a video generation job."""
    id: str
    status: JobStatus
    prompt: str
    n_variants: int
    n_seconds: int
    height: int
    width: int
    generations: List[VideoGeneration]
    finished_at: Optional[int] = None  # Unix timestamp
    failure_reason: Optional[Union[str, FailureReason]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoGenerationJob':
        """Create VideoGenerationJob from API response dictionary."""
        generations = [VideoGeneration.from_dict(
            gen) for gen in data.get("generations", [])]

        # Convert status string to enum
        status = data["status"]
        if isinstance(status, str):
            status = JobStatus(status)

        # Convert failure reason string to enum if present
        failure_reason = data.get("failure_reason")
        if isinstance(failure_reason, str) and failure_reason:
            try:
                failure_reason = FailureReason(failure_reason)
            except ValueError:
                # Keep as string if not a known enum value
                pass

        return cls(
            id=data["id"],
            status=status,
            prompt=data["prompt"],
            n_variants=data["n_variants"],
            n_seconds=data["n_seconds"],
            height=data["height"],
            width=data["width"],
            generations=generations,
            finished_at=data.get("finished_at"),
            failure_reason=failure_reason
        )

    @property
    def finished_datetime(self) -> Optional[datetime]:
        """Convert Unix timestamp to datetime."""
        if self.finished_at:
            return datetime.fromtimestamp(self.finished_at)
        return None


@dataclass
class VideoGenerationJobList:
    """List of video generation jobs."""
    data: List[VideoGenerationJob]
    has_more: bool
    first_id: str
    last_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoGenerationJobList':
        """Create VideoGenerationJobList from API response dictionary."""
        jobs = [VideoGenerationJob.from_dict(
            job) for job in data.get("data", [])]
        return cls(
            data=jobs,
            has_more=data["has_more"],
            first_id=data["first_id"],
            last_id=data["last_id"]
        )


@dataclass
class AzureOpenAIVideoGenerationError:
    """Error details for Azure OpenAI Video Generation API."""
    code: str
    message: str
    param: Optional[str] = None
    inner_error: Optional[Dict[str, Any]] = None
