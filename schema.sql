CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    tag1 TEXT,
    tag2 TEXT,
    tag3 TEXT,
    frequency TEXT NOT NULL DEFAULT '0,1,2,3,4,5,6',
    position INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    completed_on TEXT NOT NULL,
    UNIQUE (habit_id, completed_on),
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
);

-- Indexes to speed up queries that filter, group, and sort by habit/date.
CREATE INDEX IF NOT EXISTS idx_completions_habit_completed_on ON completions(habit_id, completed_on);
CREATE INDEX IF NOT EXISTS idx_habits_position ON habits(position);

-- Keep the existing date index for backward compatibility with reporting queries.
CREATE INDEX IF NOT EXISTS idx_completions_completed_on ON completions(completed_on);
