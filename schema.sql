CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    tag1 TEXT,
    tag2 TEXT,
    tag3 TEXT,
    frequency TEXT NOT NULL DEFAULT '0,1,2,3,4,5,6',
    tracking_type TEXT NOT NULL DEFAULT 'boolean',
    target_value REAL NOT NULL DEFAULT 1,
    unit TEXT,
    category TEXT NOT NULL DEFAULT 'Health',
    color TEXT NOT NULL DEFAULT '#2d7a52',
    archived INTEGER NOT NULL DEFAULT 0,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    completed_on TEXT NOT NULL,
    value REAL NOT NULL DEFAULT 1,
    note TEXT NOT NULL DEFAULT '',
    UNIQUE (habit_id, completed_on),
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
);