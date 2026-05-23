from typing import Protocol, runtime_checkable


@runtime_checkable
class BlobStore(Protocol):
    """Content-addressed storage for binary blobs (images)."""

    def put(self, data: bytes, extension: str) -> str: ...

    def get(self, image_id: str) -> bytes: ...

    def delete(self, image_id: str) -> None: ...

    def exists(self, image_id: str) -> bool: ...
