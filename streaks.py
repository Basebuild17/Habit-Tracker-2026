from datetime import date, timedelta

from db import get_db


def completion_dates(habit_id):
    rows = get_db().execute(
        "SELECT completed_on FROM completions WHERE habit_id = ? ORDER BY completed_on DESC",
        (habit_id,),
    ).fetchall()
    return {date.fromisoformat(row["completed_on"]) for row in rows}


def current_streak(habit_id, today=None):
    today = today or date.today()
    dates = completion_dates(habit_id)
    cursor = today
    streak = 0
    while cursor in dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def scheduled_days(habit):
    return {int(day) for day in (habit["frequency"] or "0,1,2,3,4,5,6").split(",") if day}


def current_streak_for_schedule(habit_id, frequency, today=None):
    today = today or date.today()
    dates = completion_dates(habit_id)
    scheduled = {int(day) for day in frequency.split(",") if day}
    cursor = today
    streak = 0
    while True:
        if cursor.weekday() in scheduled:
            if cursor not in dates:
                break
            streak += 1
        cursor -= timedelta(days=1)
        if cursor < today - timedelta(days=90):
            break
    return streak


def weekly_completion(start, end):
    rows = get_db().execute(
        """
        SELECT completed_on, COUNT(*) AS completed
        FROM completions
        WHERE completed_on BETWEEN ? AND ?
        GROUP BY completed_on
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    counts = {row["completed_on"]: row["completed"] for row in rows}
    days = []
    cursor = start
    while cursor <= end:
        days.append({"date": cursor, "completed": counts.get(cursor.isoformat(), 0)})
        cursor += timedelta(days=1)
    return days


def history_for_habit(habit_id, start, end):
    rows = get_db().execute(
        "SELECT completed_on FROM completions WHERE habit_id = ? AND completed_on BETWEEN ? AND ?",
        (habit_id, start.isoformat(), end.isoformat()),
    ).fetchall()
    return {date.fromisoformat(row["completed_on"]) for row in rows}