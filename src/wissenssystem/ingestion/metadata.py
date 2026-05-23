from pydantic import BaseModel


class IngestReport(BaseModel):
    """Summary of a completed ingestion run."""

    doc_id: str
    namespace: str
    chunks_count: int
    images_count: int
    menu_paths_count: int
    safety_notices_count: int
