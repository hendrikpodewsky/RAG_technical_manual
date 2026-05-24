"""Seed the machine registry from data/machines.yaml.

Usage:
    python -m wissenssystem.cli.seed_registry [--db PATH] [--yaml PATH]
"""

import argparse
import sys
import uuid
from pathlib import Path

import yaml

from wissenssystem.domain.machine import Configuration, Machine
from wissenssystem.registry.machine_registry import MachineRegistry


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _seed(db_path: str, yaml_path: Path) -> None:
    data = _load_yaml(yaml_path)
    registry = MachineRegistry(db_path)

    for entry in data.get("machines", []):
        cfg_data = entry["configuration"]
        config = Configuration(
            namespace=cfg_data["namespace"],
            manufacturer=cfg_data["manufacturer"],
            model_family=cfg_data["model_family"],
            indoor_unit=cfg_data.get("indoor_unit"),
            outdoor_unit=cfg_data.get("outdoor_unit"),
            software_version=cfg_data.get("software_version"),
            country=cfg_data["country"],
        )
        registry.register_configuration(config)

        machine = Machine(
            machine_id=str(uuid.uuid4()),
            name=entry["name"],
            aliases=entry.get("aliases", []),
            location=entry.get("location"),
            responsible=entry.get("responsible"),
            configuration_namespace=cfg_data["namespace"],
        )
        registry.register_machine(machine)
        print(f"  registered: {machine.name} ({cfg_data['namespace']})")

    registry.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed machine registry from YAML")
    parser.add_argument("--db", default="data/registry.db", help="Path to SQLite DB")
    parser.add_argument(
        "--yaml",
        default="data/machines.yaml",
        help="Path to machines YAML file",
    )
    args = parser.parse_args()

    yaml_path = Path(args.yaml)
    if not yaml_path.exists():
        print(f"Error: YAML file not found: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Seeding registry from {yaml_path} → {args.db}")
    _seed(args.db, yaml_path)
    print("Done.")


if __name__ == "__main__":
    main()
