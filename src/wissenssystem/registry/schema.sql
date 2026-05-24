-- Registry schema — idempotent (CREATE IF NOT EXISTS everywhere)

CREATE TABLE IF NOT EXISTS configurations (
    namespace        TEXT PRIMARY KEY,
    manufacturer     TEXT NOT NULL,
    model_family     TEXT NOT NULL,
    indoor_unit      TEXT,
    outdoor_unit     TEXT,
    software_version TEXT,
    country          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS machines (
    machine_id               TEXT PRIMARY KEY,
    name                     TEXT NOT NULL,
    location                 TEXT,
    responsible              TEXT,
    configuration_namespace  TEXT NOT NULL REFERENCES configurations(namespace)
);

CREATE TABLE IF NOT EXISTS machine_aliases (
    machine_id  TEXT NOT NULL REFERENCES machines(machine_id) ON DELETE CASCADE,
    alias       TEXT NOT NULL,
    PRIMARY KEY (machine_id, alias)
);

CREATE INDEX IF NOT EXISTS idx_machine_aliases_alias ON machine_aliases(alias);

CREATE TABLE IF NOT EXISTS menu_paths (
    path_id          TEXT PRIMARY KEY,
    namespace        TEXT NOT NULL,
    nodes            TEXT NOT NULL,   -- JSON array of strings
    leaf_description TEXT NOT NULL,
    page             INTEGER NOT NULL,
    section_path     TEXT NOT NULL    -- JSON array of strings
);

CREATE INDEX IF NOT EXISTS idx_menu_paths_namespace ON menu_paths(namespace);
