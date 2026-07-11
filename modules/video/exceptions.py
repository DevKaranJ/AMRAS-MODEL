from app.core.exceptions import AmrasException


class VideoException(AmrasException):
    """Base exception for video rendering module."""

    def __init__(self, message: str, error_code: str = "VIDEO_ERROR", retry_hint: str | None = None):
        super().__init__(message=message, error_code=error_code, recovery_suggestion=retry_hint)


class RenderJobNotFound(VideoException):
    def __init__(self, job_id: int):
        super().__init__(
            message=f"Render job {job_id} not found.",
            error_code="RENDER_JOB_NOT_FOUND",
            retry_hint="Verify the job ID is correct.",
        )


class SceneRenderError(VideoException):
    def __init__(self, scene_id: int, reason: str):
        super().__init__(
            message=f"Failed to render scene {scene_id}: {reason}",
            error_code="SCENE_RENDER_ERROR",
            retry_hint="Check scene assets and configuration.",
        )


class EncodingError(VideoException):
    def __init__(self, reason: str):
        super().__init__(
            message=f"Video encoding failed: {reason}",
            error_code="ENCODING_ERROR",
            retry_hint="Check disk space and codec settings.",
        )


class ResourceExhaustedError(VideoException):
    def __init__(self, resource: str):
        super().__init__(
            message=f"Resource exhausted during rendering: {resource}",
            error_code="RESOURCE_EXHAUSTED",
            retry_hint="Lower render quality or free up system resources.",
        )


class QAValidationError(VideoException):
    def __init__(self, reason: str):
        super().__init__(
            message=f"Rendered video failed QA validation: {reason}",
            error_code="QA_VALIDATION_ERROR",
            retry_hint="Check for missing frames or audio sync issues.",
        )


class InvalidRenderActionError(VideoException):
    def __init__(self, action: str):
        super().__init__(
            message=f"Invalid render action: {action}",
            error_code="INVALID_RENDER_ACTION",
            retry_hint="Use one of the supported actions: 'start', 'resume', 'cancel', 'status'.",
        )
