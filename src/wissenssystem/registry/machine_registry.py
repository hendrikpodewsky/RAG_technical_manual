import json
import sqlite3
import uuid
from pathlib import Path

from wissenssystem.domain.machine import Configuration, Machine
from wissenssystem.domain.menu_path import MenuPath
from wissenssystem.domain.source import SourceRef

_SCHEMA = Path(__file__).parent / "schema.sql"


class MachineRegistry:
    """SQLite-backed registry for machines, configurations, and menu paths.

    All mutations are auto-committed. Pass db_path=':memory:' for tests.
    """

    def __init__(self, db_path: str | Path = "data/registry.db") -> None:
        self._con = sqlite3.connect(str(db_path), check_same_thread=False)
        self._con.row_factory = sqlite3.Row
        self._con.execute("PRAGMA foreign_keys = ON")
        self._migrate()

    def close(self) -> None:
        self._con.close()

    def _migrate(self) -> None:
        self._con.executescript(_SCHEMA.read_text())
        self._con.commit()

    # --- Configurations ---

    def register_configuration(self, config: Configuration) -> None:
        self._con.execute(
            """
            INSERT OR REPLACE INTO configurations
              (namespace, manufacturer, model_family, indoor_unit,
               outdoor_unit, software_version, country)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                config.namespace,
                config.manufacturer,
                config.model_family,
                config.indoor_unit,
                config.outdoor_unit,
                config.software_version,
                config.country,
            ),
        )
        self._con.commit()

    def get_configuration(self, namespace: str) -> Configuration | None:
        row = self._con.execute(
            "SELECT * FROM configurations WHERE namespace = ?", (namespace,)
        ).fetchone()
        return _row_to_config(row) if row else None

    def list_configurations(self) -> list[Configuration]:
        rows = self._con.execute("SELECT * FROM configurations").fetchall()
        return [_row_to_config(r) for r in rows]

    # --- Machines ---

    def register_machine(self, machine: Machine) -> None:
        self._con.execute(
            """
            INSERT OR REPLACE INTO machines
              (machine_id, name, location, responsible, configuration_namespace)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                machine.machine_id,
                machine.name,
                machine.location,
                machine.responsible,
                machine.configuration_namespace,
            ),
        )
        # Replace aliases: delete existing, re-insert
        self._con.execute(
            "DELETE FROM machine_aliases WHERE machine_id = ?", (machine.machine_id,)
        )
        self._con.executemany(
            "INSERT INTO machine_aliases (machine_id, alias) VALUES (?, ?)",
            [(machine.machine_id, a) for a in machine.aliases],
        )
        self._con.commit()

    def get_machine(self, machine_id: str) -> Machine | None:
        row = self._con.execute(
            "SELECT * FROM machines WHERE machine_id = ?", (machine_id,)
        ).fetchone()
        if not row:
            return None
        aliases = self._load_aliases(machine_id)
        return _row_to_machine(row, aliases)

    def find_by_alias(self, alias: str) -> list[Machine]:
        """Case-insensitive prefix search on aliases."""
        rows = self._con.execute(
            """
            SELECT m.* FROM machines m
            JOIN machine_aliases a ON m.machine_id = a.machine_id
            WHERE lower(a.alias) LIKE lower(?) || '%'
            """,
            (alias,),
        ).fetchall()
        return [_row_to_machine(r, self._load_aliases(r["machine_id"])) for r in rows]

    def find_by_name(self, name: str) -> list[Machine]:
        """Case-insensitive partial match on machine name."""
        rows = self._con.execute(
            "SELECT * FROM machines WHERE lower(name) LIKE '%' || lower(?) || '%'",
            (name,),
        ).fetchall()
        return [_row_to_machine(r, self._load_aliases(r["machine_id"])) for r in rows]

    def list_machines(self) -> list[Machine]:
        rows = self._con.execute("SELECT * FROM machines").fetchall()
        return [_row_to_machine(r, self._load_aliases(r["machine_id"])) for r in rows]

    def delete_machine(self, machine_id: str) -> None:
        self._con.execute("DELETE FROM machines WHERE machine_id = ?", (machine_id,))
        self._con.commit()

    def _load_aliases(self, machine_id: str) -> list[str]:
        rows = self._con.execute(
            "SELECT alias FROM machine_aliases WHERE machine_id = ?", (machine_id,)
        ).fetchall()
        return [r["alias"] for r in rows]

    # --- Menu Paths ---

    def store_menu_paths(self, paths: list[MenuPath]) -> None:
        """Upsert menu paths (replace existing by path_id)."""
        self._con.executemany(
            """
            INSERT OR REPLACE INTO menu_paths
              (path_id, namespace, nodes, leaf_description, page, section_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    p.path_id,
                    p.namespace,
                    json.dumps(p.nodes, ensure_ascii=False),
                    p.leaf_description,
                    p.source_ref.page,
                    json.dumps(p.source_ref.section_path, ensure_ascii=False),
                )
                for p in paths
            ],
        )
        self._con.commit()

    def get_menu_paths(self, namespace: str) -> list[MenuPath]:
        rows = self._con.execute(
            "SELECT * FROM menu_paths WHERE namespace = ?", (namespace,)
        ).fetchall()
        return [_row_to_menu_path(r) for r in rows]

    def delete_menu_paths(self, namespace: str) -> None:
        self._con.execute("DELETE FROM menu_paths WHERE namespace = ?", (namespace,))
        self._con.commit()


# --- helpers ---


def _row_to_config(row: sqlite3.Row) -> Configuration:
    return Configuration(
        namespace=row["namespace"],
        manufacturer=row["manufacturer"],
        model_family=row["model_family"],
        indoor_unit=row["indoor_unit"],
        outdoor_unit=row["outdoor_unit"],
        software_version=row["software_version"],
        country=row["country"],
    )


def _row_to_machine(row: sqlite3.Row, aliases: list[str]) -> Machine:
    return Machine(
        machine_id=row["machine_id"],
        name=row["name"],
        aliases=aliases,
        location=row["location"],
        responsible=row["responsible"],
        configuration_namespace=row["configuration_namespace"],
    )


def _row_to_menu_path(row: sqlite3.Row) -> MenuPath:
    return MenuPath(
        path_id=row["path_id"],
        namespace=row["namespace"],
        nodes=json.loads(row["nodes"]),
        leaf_description=row["leaf_description"],
        source_ref=SourceRef(
            doc_id="",
            page=row["page"],
            section_path=json.loads(row["section_path"]),
        ),
    )


def new_machine_id() -> str:
    return str(uuid.uuid4())
