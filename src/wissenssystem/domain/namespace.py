import re

from wissenssystem.domain.machine import Configuration

_SEPARATOR = "__"
_NONE_PLACEHOLDER = "none"
_ALLOWED = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


def _slugify(value: str) -> str:
    """Lowercase, collapse whitespace to hyphens, strip non-alphanumeric except hyphens."""
    slug = value.strip().lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug or _NONE_PLACEHOLDER


def build_namespace(
    manufacturer: str,
    model_family: str,
    sw_version: str | None,
    country: str,
) -> str:
    """Build a canonical namespace string from configuration components.

    Format: cfg__<manufacturer>__<model_family>__<sw_version>__<country>
    """
    parts = [
        "cfg",
        _slugify(manufacturer),
        _slugify(model_family),
        _slugify(sw_version) if sw_version else _NONE_PLACEHOLDER,
        _slugify(country),
    ]
    return _SEPARATOR.join(parts)


def parse_namespace(ns: str) -> Configuration:
    """Parse a namespace string back into a Configuration.

    Raises ValueError for malformed namespaces.
    """
    parts = ns.split(_SEPARATOR)
    if len(parts) != 5 or parts[0] != "cfg":
        raise ValueError(f"Invalid namespace format: {ns!r}")

    _, manufacturer, model_family, sw_version_raw, country = parts

    if not all(p for p in [manufacturer, model_family, sw_version_raw, country]):
        raise ValueError(f"Empty segment in namespace: {ns!r}")

    sw_version = None if sw_version_raw == _NONE_PLACEHOLDER else sw_version_raw

    return Configuration(
        namespace=ns,
        manufacturer=manufacturer,
        model_family=model_family,
        indoor_unit=None,
        outdoor_unit=None,
        software_version=sw_version,
        country=country,
    )
