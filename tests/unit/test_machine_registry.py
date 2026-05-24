import pytest

from wissenssystem.domain.machine import Configuration, Machine
from wissenssystem.domain.menu_path import MenuPath
from wissenssystem.domain.source import SourceRef
from wissenssystem.registry.machine_registry import MachineRegistry, new_machine_id

NS = "cfg__bosch__ui800__nf87-02__de"


@pytest.fixture
def reg() -> MachineRegistry:
    return MachineRegistry(":memory:")


def _config(ns: str = NS) -> Configuration:
    return Configuration(
        namespace=ns,
        manufacturer="Bosch",
        model_family="UI 800",
        indoor_unit=None,
        outdoor_unit=None,
        software_version="NF87.02",
        country="DE",
    )


def _machine(machine_id: str | None = None, aliases: list[str] | None = None) -> Machine:
    return Machine(
        machine_id=machine_id or new_machine_id(),
        name="Wärmepumpe Halle 2",
        aliases=aliases or ["WP Halle 2", "die hintere Pumpe"],
        location="Halle 2",
        responsible="Technik",
        configuration_namespace=NS,
    )


def _menu_path(path_id: str = "p1", nodes: list[str] | None = None) -> MenuPath:
    return MenuPath(
        path_id=path_id,
        namespace=NS,
        nodes=nodes or ["Service", "Einstellung"],
        leaf_description="Einstellung",
        source_ref=SourceRef(doc_id="", page=45, section_path=["8"]),
    )


# --- Schema migration is idempotent ---


def test_double_migrate_does_not_raise():
    reg = MachineRegistry(":memory:")
    reg._migrate()  # second time must be idempotent


# --- Configurations ---


def test_register_and_get_configuration(reg):
    cfg = _config()
    reg.register_configuration(cfg)
    result = reg.get_configuration(NS)
    assert result is not None
    assert result.manufacturer == "Bosch"
    assert result.software_version == "NF87.02"


def test_get_configuration_missing_returns_none(reg):
    assert reg.get_configuration("nonexistent") is None


def test_list_configurations(reg):
    reg.register_configuration(_config())
    reg.register_configuration(_config("cfg__test__x__1__at"))
    assert len(reg.list_configurations()) == 2


def test_register_configuration_replace(reg):
    cfg = _config()
    reg.register_configuration(cfg)
    updated = Configuration(
        namespace=NS,
        manufacturer="Bosch",
        model_family="UI 800",
        indoor_unit="CS7000iAW 9 OR-S",
        outdoor_unit=None,
        software_version="NF88",
        country="DE",
    )
    reg.register_configuration(updated)
    result = reg.get_configuration(NS)
    assert result is not None
    assert result.software_version == "NF88"
    assert result.indoor_unit == "CS7000iAW 9 OR-S"


# --- Machines ---


def test_register_and_get_machine(reg):
    reg.register_configuration(_config())
    m = _machine()
    reg.register_machine(m)
    result = reg.get_machine(m.machine_id)
    assert result is not None
    assert result.name == "Wärmepumpe Halle 2"
    assert "WP Halle 2" in result.aliases


def test_get_machine_missing_returns_none(reg):
    assert reg.get_machine("does-not-exist") is None


def test_list_machines(reg):
    reg.register_configuration(_config())
    reg.register_machine(_machine("id1"))
    reg.register_machine(_machine("id2"))
    assert len(reg.list_machines()) == 2


def test_delete_machine(reg):
    reg.register_configuration(_config())
    m = _machine()
    reg.register_machine(m)
    reg.delete_machine(m.machine_id)
    assert reg.get_machine(m.machine_id) is None


def test_aliases_deleted_with_machine(reg):
    reg.register_configuration(_config())
    m = _machine("id1", aliases=["alias1"])
    reg.register_machine(m)
    reg.delete_machine("id1")
    assert reg.find_by_alias("alias1") == []


# --- Alias search ---


def test_find_by_alias_exact(reg):
    reg.register_configuration(_config())
    reg.register_machine(_machine(aliases=["WP Halle 2"]))
    results = reg.find_by_alias("WP Halle 2")
    assert len(results) == 1


def test_find_by_alias_prefix(reg):
    reg.register_configuration(_config())
    reg.register_machine(_machine(aliases=["WP Halle 2"]))
    results = reg.find_by_alias("WP Hall")
    assert len(results) == 1


def test_find_by_alias_case_insensitive(reg):
    reg.register_configuration(_config())
    reg.register_machine(_machine(aliases=["wp halle 2"]))
    results = reg.find_by_alias("WP Halle")
    assert len(results) == 1


def test_find_by_alias_no_match(reg):
    reg.register_configuration(_config())
    reg.register_machine(_machine(aliases=["WP Halle 2"]))
    assert reg.find_by_alias("Kompressor") == []


def test_find_by_name_partial(reg):
    reg.register_configuration(_config())
    reg.register_machine(_machine())
    results = reg.find_by_name("Halle")
    assert len(results) == 1


# --- Menu Paths ---


def test_store_and_get_menu_paths(reg):
    path = _menu_path()
    reg.store_menu_paths([path])
    results = reg.get_menu_paths(NS)
    assert len(results) == 1
    assert results[0].nodes == ["Service", "Einstellung"]


def test_store_menu_paths_upsert(reg):
    reg.store_menu_paths([_menu_path("p1", ["Service", "A"])])
    reg.store_menu_paths([_menu_path("p1", ["Service", "B"])])
    results = reg.get_menu_paths(NS)
    assert len(results) == 1
    assert results[0].nodes == ["Service", "B"]


def test_get_menu_paths_filters_by_namespace(reg):
    reg.store_menu_paths([_menu_path("p1")])
    other_path = MenuPath(
        path_id="p2",
        namespace="other__ns",
        nodes=["Menu"],
        leaf_description="Menu",
        source_ref=SourceRef(doc_id="", page=1, section_path=["1"]),
    )
    reg.store_menu_paths([other_path])
    assert len(reg.get_menu_paths(NS)) == 1
    assert len(reg.get_menu_paths("other__ns")) == 1


def test_delete_menu_paths(reg):
    reg.store_menu_paths([_menu_path("p1"), _menu_path("p2")])
    reg.delete_menu_paths(NS)
    assert reg.get_menu_paths(NS) == []


def test_menu_path_source_ref_preserved(reg):
    path = _menu_path()
    reg.store_menu_paths([path])
    result = reg.get_menu_paths(NS)[0]
    assert result.source_ref.page == 45
    assert result.source_ref.section_path == ["8"]
