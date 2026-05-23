import hashlib
from pathlib import Path


class BlobNotFoundError(Exception):
    """Raised when a requested blob does not exist in the store."""


class LocalBlobStore:
    """Content-addressed file storage under a configurable base directory.

    image_id is the SHA-256 hex digest of the content; equal content always
    produces the same ID (idempotent puts).
    """

    def __init__(self, base_dir: Path) -> None:
        self._base = base_dir
        self._base.mkdir(parents=True, exist_ok=True)

    def _path(self, image_id: str, extension: str = "") -> Path:
        suffix = f".{extension}" if extension else ""
        return self._base / f"{image_id}{suffix}"

    def _find(self, image_id: str) -> Path:
        matches = list(self._base.glob(f"{image_id}.*"))
        if not matches:
            raise BlobNotFoundError(f"Blob not found: {image_id!r}")
        return matches[0]

    def put(self, data: bytes, extension: str) -> str:
        image_id = hashlib.sha256(data).hexdigest()
        target = self._path(image_id, extension)
        if not target.exists():
            target.write_bytes(data)
        return image_id

    def get(self, image_id: str) -> bytes:
        return self._find(image_id).read_bytes()

    def delete(self, image_id: str) -> None:
        self._find(image_id).unlink()

    def exists(self, image_id: str) -> bool:
        return bool(list(self._base.glob(f"{image_id}.*")))
