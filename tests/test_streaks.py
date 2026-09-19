from datetime import date, timedelta

from db import get_db
from streaks import current_streak


def test_current_streak_counts_backwards_from_today(app):
    with app.app_context():
        database = get_db()
        database.execute("INSERT INTO habits (name) VALUES (?)", ("Read",))
        habit_id = database.execute("SELECT last_insert_rowid()").fetchone()[0]
        for offset in range(3):
            database.execute(
                "INSERT INTO completions (habit_id, completed_on) VALUES (?, ?)",
                (habit_id, (date.today() - timedelta(days=offset)).isoformat()),
            )
        database.commit()
        assert current_streak(habit_id) == 3


def test_current_streak_is_zero_when_today_is_missing(app):
    with app.app_context():
        database = get_db()
        database.execute("INSERT INTO habits (name) VALUES (?)", ("Stretch",))
        database.commit()
        assert current_streak(1) == 0