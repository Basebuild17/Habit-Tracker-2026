import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(Path(current_app.config["DATABASE"]))
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    schema = Path(current_app.root_path, "schema.sql").read_text()
    db.executescript(schema)
    columns = {row["name"] for row in db.execute("PRAGMA table_info(habits)").fetchall()}
    migrations = {
        "tag1": "ALTER TABLE habits ADD COLUMN tag1 TEXT",
        "tag2": "ALTER TABLE habits ADD COLUMN tag2 TEXT",
        "tag3": "ALTER TABLE habits ADD COLUMN tag3 TEXT",
        "frequency": "ALTER TABLE habits ADD COLUMN frequency TEXT NOT NULL DEFAULT '0,1,2,3,4,5,6'",
        "tracking_type": "ALTER TABLE habits ADD COLUMN tracking_type TEXT NOT NULL DEFAULT 'boolean'",
        "target_value": "ALTER TABLE habits ADD COLUMN target_value REAL NOT NULL DEFAULT 1",
        "unit": "ALTER TABLE habits ADD COLUMN unit TEXT",
        "category": "ALTER TABLE habits ADD COLUMN category TEXT NOT NULL DEFAULT 'Health'",
        "color": "ALTER TABLE habits ADD COLUMN color TEXT NOT NULL DEFAULT '#2d7a52'",
        "archived": "ALTER TABLE habits ADD COLUMN archived INTEGER NOT NULL DEFAULT 0",
        "position": "ALTER TABLE habits ADD COLUMN position INTEGER NOT NULL DEFAULT 0",
    }
    for column, statement in migrations.items():
        if column not in columns:
            db.execute(statement)
    completion_columns = {row["name"] for row in db.execute("PRAGMA table_info(completions)").fetchall()}
    for column, statement in {
        "value": "ALTER TABLE completions ADD COLUMN value REAL NOT NULL DEFAULT 1",
        "note": "ALTER TABLE completions ADD COLUMN note TEXT NOT NULL DEFAULT ''",
    }.items():
        if column not in completion_columns:
            db.execute(statement)
    db.execute("UPDATE habits SET position = id WHERE position = 0")
    db.commit()