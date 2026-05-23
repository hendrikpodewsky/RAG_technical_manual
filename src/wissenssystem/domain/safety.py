from enum import Enum

from pydantic import BaseModel, ConfigDict


class SafetyLevel(str, Enum):
    """Severity levels for safety notices as defined in machine manuals."""

    GEFAHR = "GEFAHR"
    WARNUNG = "WARNUNG"
    VORSICHT = "VORSICHT"
    ACHTUNG = "ACHTUNG"
    HINWEIS = "HINWEIS"


class SafetyNotice(BaseModel):
    """A safety-relevant block extracted verbatim from a manual."""

    level: SafetyLevel
    raw_text: str

    model_config = ConfigDict(frozen=True)
