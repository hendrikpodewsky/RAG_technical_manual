from pydantic import BaseModel, ConfigDict


class Configuration(BaseModel):
    """A unique combination of model, software version and country that maps to one namespace."""

    namespace: str
    manufacturer: str
    model_family: str
    indoor_unit: str | None
    outdoor_unit: str | None
    software_version: str | None
    country: str

    model_config = ConfigDict(frozen=True)


class Machine(BaseModel):
    """A physical device installation with aliases, location and a configuration reference."""

    machine_id: str
    name: str
    aliases: list[str]
    location: str | None
    responsible: str | None
    configuration_namespace: str

    model_config = ConfigDict(frozen=True)
