from typing import Protocol, runtime_checkable


@runtime_checkable
class VisionProvider(Protocol):
    """Generates textual descriptions of images."""

    def describe_image(
        self,
        image: bytes,
        media_type: str,
        context: str,
        prompt: str,
    ) -> str: ...
