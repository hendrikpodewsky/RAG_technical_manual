from pathlib import Path

from pydantic import BaseModel, ConfigDict


class SourceDocument(BaseModel):
    """A physical PDF source document ingested into the system."""

    doc_id: str
    title: str
    publisher: str
    document_number: str
    edition: str
    software_version: str | None
    country_codes: list[str]
    pdf_path: Path
    config_namespace: str

    model_config = ConfigDict(frozen=True)


class SourceRef(BaseModel):
    """A precise reference to a location within a source document."""

    doc_id: str
    page: int
    section_path: list[str]

    model_config = ConfigDict(frozen=True)
