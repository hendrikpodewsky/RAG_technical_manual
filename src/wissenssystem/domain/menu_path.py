from pydantic import BaseModel, ConfigDict

from wissenssystem.domain.source import SourceRef


class MenuNode(BaseModel):
    """A single node in a device menu hierarchy."""

    label: str
    children: list["MenuNode"] = []

    model_config = ConfigDict(frozen=True)


class MenuPath(BaseModel):
    """A complete path through the device menu to a specific setting."""

    path_id: str
    nodes: list[str]
    leaf_description: str
    source_ref: SourceRef
    namespace: str

    model_config = ConfigDict(frozen=True)
