from datetime import date, timedelta

from db import get_db
from streaks import current_streak, current_streak_for_schedule


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


def test_scheduled_streak_has_no_90_day_limit(app):
    today = date(2026, 10, 3)
    with app.app_context():
        database = get_db()
        database.execute("INSERT INTO habits (name) VALUES (?)", ("Daily habit",))
        habit_id = database.execute("SELECT last_insert_rowid()").fetchone()[0]
        database.executemany(
            "INSERT INTO completions (habit_id, completed_on) VALUES (?, ?)",
            [
                (habit_id, (today - timedelta(days=offset)).isoformat())
                for offset in range(100)
            ],
        )
        database.commit()

        assert current_streak_for_schedule(habit_id, "0,1,2,3,4,5,6", today) == 100


def test_scheduled_streak_is_zero_for_empty_schedule(app):
    with app.app_context():
        database = get_db()
        database.execute("INSERT INTO habits (name) VALUES (?)", ("Unscheduled",))
        database.commit()

        assert current_streak_for_schedule(1, "") == 0