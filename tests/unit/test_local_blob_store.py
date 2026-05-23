import pytest

from wissenssystem.interfaces.blob_store import BlobStore
from wissenssystem.providers.local_blob_store import BlobNotFoundError, LocalBlobStore


@pytest.fixture
def store(tmp_path):
    return LocalBlobStore(tmp_path / "blobs")


def test_implements_protocol(store):
    assert isinstance(store, BlobStore)


def test_put_returns_sha256(store):
    image_id = store.put(b"\x89PNG", "png")
    assert len(image_id) == 64
    assert all(c in "0123456789abcdef" for c in image_id)


def test_put_idempotent(store):
    data = b"same content"
    id1 = store.put(data, "png")
    id2 = store.put(data, "png")
    assert id1 == id2
    assert len(list((store._base).glob("*.png"))) == 1


def test_get_returns_original_content(store):
    data = b"\x89PNG\r\n\x1a\nfakeimage"
    image_id = store.put(data, "png")
    assert store.get(image_id) == data


def test_roundtrip_different_extensions(store):
    png_data = b"png content"
    jpg_data = b"jpg content"
    png_id = store.put(png_data, "png")
    jpg_id = store.put(jpg_data, "jpg")
    assert store.get(png_id) == png_data
    assert store.get(jpg_id) == jpg_data


def test_exists_true_after_put(store):
    image_id = store.put(b"data", "jpg")
    assert store.exists(image_id) is True


def test_exists_false_for_unknown(store):
    assert store.exists("a" * 64) is False


def test_delete_removes_blob(store):
    image_id = store.put(b"to delete", "png")
    store.delete(image_id)
    assert store.exists(image_id) is False


def test_get_raises_on_missing(store):
    with pytest.raises(BlobNotFoundError):
        store.get("a" * 64)


def test_delete_raises_on_missing(store):
    with pytest.raises(BlobNotFoundError):
        store.delete("b" * 64)


def test_creates_base_dir_if_missing(tmp_path):
    nested = tmp_path / "deep" / "nested" / "blobs"
    store = LocalBlobStore(nested)
    assert nested.exists()
    image_id = store.put(b"hello", "txt")
    assert store.exists(image_id)
