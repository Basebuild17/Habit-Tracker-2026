import os
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, flash, redirect, render_template, request, url_for

from .db import close_db, get_db, init_db
from .streaks import weekly_completion


WEEKDAYS = [(0, "Mon"), (1, "Tue"), (2, "Wed"), (3, "Thu"), (4, "Fri"), (5, "Sat"), (6, "Sun")]


def parse_frequency(frequency):
    if not frequency:
        return set(range(7))
    return {int(day) for day in str(frequency).split(",") if day}


def compute_streak_from_dates(completed_dates, frequency):
    scheduled = parse_frequency(frequency)
    if not scheduled:
        return 0
    cursor = date.today()
    streak = 0
    while True:
        if cursor.weekday() in scheduled:
            if cursor not in completed_dates:
                break
            streak += 1
        cursor -= timedelta(days=1)
    return streak


def habit_form_values(form):
    tags = [form.get(f"tag{index}", "").strip()[:24] for index in range(1, 4)]
    frequency = sorted({int(day) for day in form.getlist("frequency") if day.isdigit() and 0 <= int(day) <= 6})
    return tags, ",".join(str(day) for day in frequency) or "0,1,2,3,4,5,6"


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    default_db = Path(os.environ.get("HABIT_TRACKER_DB", Path.home() / ".habit_tracker" / "habits.sqlite"))
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=str(default_db),
    )

    if test_config is not None:
        app.config.update(test_config)

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    @app.get("/")
    def index():
        today = date.today().isoformat()
        db = get_db()
        habits = db.execute(
            """
            SELECT h.id, h.name,
                     EXISTS (
                        SELECT 1 FROM completions c
                        WHERE c.habit_id = h.id AND c.completed_on = ?
                      ) AS completed_today, h.tag1, h.tag2, h.tag3, h.frequency
            FROM habits h
                 ORDER BY h.position, h.id
            """,
            (today,),
        ).fetchall()

        habit_ids = [habit["id"] for habit in habits]
        completions_by_habit = {}
        if habit_ids:
            placeholders = ",".join("?" for _ in habit_ids)
            rows = db.execute(
                f"SELECT habit_id, completed_on FROM completions WHERE habit_id IN ({placeholders})",
                habit_ids,
            ).fetchall()
            for row in rows:
                completions_by_habit.setdefault(row["habit_id"], set()).add(date.fromisoformat(row["completed_on"]))

        habit_cards = [
            {
                "id": habit["id"],
                "name": habit["name"],
                "completed_today": bool(habit["completed_today"]),
                "streak": compute_streak_from_dates(completions_by_habit.get(habit["id"], set()), habit["frequency"]),
                "tags": [tag for tag in (habit["tag1"], habit["tag2"], habit["tag3"]) if tag],
                "frequency": parse_frequency(habit["frequency"]),
            }
            for habit in habits
        ]
        return render_template(
            "index.html",
            habits=habit_cards,
            today=date.today().strftime("%A, %B %d"),
            weekdays=WEEKDAYS,
            completed_count=sum(habit["completed_today"] for habit in habit_cards),
        )

    @app.post("/habits")
    def add_habit():
        name = request.form.get("name", "").strip()
        tags, frequency = habit_form_values(request.form)
        if not name:
            flash("Give your habit a name first.", "error")
        elif len(name) > 80:
            flash("Habit names must be 80 characters or fewer.", "error")
        else:
            db = get_db()
            position = db.execute("SELECT COALESCE(MAX(position), -1) + 1 FROM habits").fetchone()[0]
            db.execute(
                "INSERT INTO habits (name, tag1, tag2, tag3, frequency, position) VALUES (?, ?, ?, ?, ?, ?)",
                (name, *tags, frequency, position),
            )
            db.commit()
            flash(f'Added "{name}".', "success")
        return redirect(url_for("index"))

    @app.post("/habits/<int:habit_id>/toggle")
    def toggle_habit(habit_id):
        db = get_db()
        habit = db.execute("SELECT name FROM habits WHERE id = ?", (habit_id,)).fetchone()
        if habit is None:
            flash("That habit no longer exists.", "error")
            return redirect(url_for("index"))

        today = date.today().isoformat()
        completion = db.execute(
            "SELECT 1 FROM completions WHERE habit_id = ? AND completed_on = ?",
            (habit_id, today),
        ).fetchone()
        if completion:
            db.execute(
                "DELETE FROM completions WHERE habit_id = ? AND completed_on = ?",
                (habit_id, today),
            )
        else:
            db.execute(
                "INSERT INTO completions (habit_id, completed_on) VALUES (?, ?)",
                (habit_id, today),
            )
        db.commit()
        return redirect(url_for("index"))

    @app.route("/habits/<int:habit_id>/edit", methods=["GET", "POST"])
    def edit_habit(habit_id):
        db = get_db()
        habit = db.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
        if habit is None:
            flash("That habit no longer exists.", "error")
            return redirect(url_for("index"))
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            tags, frequency = habit_form_values(request.form)
            if not name or len(name) > 80:
                flash("Use a habit name between 1 and 80 characters.", "error")
            else:
                db.execute(
                    "UPDATE habits SET name = ?, tag1 = ?, tag2 = ?, tag3 = ?, frequency = ? WHERE id = ?",
                    (name, *tags, frequency, habit_id),
                )
                db.commit()
                flash("Habit updated.", "success")
                return redirect(url_for("index"))
        return render_template("edit.html", habit=habit, weekdays=WEEKDAYS)

    @app.post("/habits/<int:habit_id>/move/<direction>")
    def move_habit(habit_id, direction):
        db = get_db()
        habit = db.execute("SELECT id, position FROM habits WHERE id = ?", (habit_id,)).fetchone()
        if habit:
            operator = "<" if direction == "up" else ">"
            order = "DESC" if direction == "up" else "ASC"
            neighbor = db.execute(
                f"SELECT id, position FROM habits WHERE position {operator} ? ORDER BY position {order} LIMIT 1",
                (habit["position"],),
            ).fetchone()
            if neighbor:
                db.execute("UPDATE habits SET position = ? WHERE id = ?", (neighbor["position"], habit_id))
                db.execute("UPDATE habits SET position = ? WHERE id = ?", (habit["position"], neighbor["id"]))
                db.commit()
        return redirect(url_for("index"))

    @app.post("/habits/<int:habit_id>/delete")
    def delete_habit(habit_id):
        db = get_db()
        db.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        db.commit()
        flash("Habit deleted.", "success")
        return redirect(url_for("index"))

    @app.get("/stats")
    def stats():
        end = date.today()
        start = end - timedelta(days=6)
        rows = weekly_completion(start, end)
        total = sum(row["completed"] for row in rows)
        db = get_db()
        frequency_sets = [parse_frequency(row["frequency"]) for row in db.execute("SELECT frequency FROM habits").fetchall()]
        possible = sum(
            1
            for row in rows
            for frequency_set in frequency_sets
            if row["date"].weekday() in frequency_set
        )
        return render_template(
            "stats.html",
            days=rows,
            total=total,
            possible=possible,
        )

    @app.get("/history")
    def history():
        end = date.today()
        start = end - timedelta(days=29)
        db = get_db()
        habits = db.execute("SELECT id, name, tag1, tag2, tag3 FROM habits ORDER BY position, id").fetchall()

        habit_ids = [habit["id"] for habit in habits]
        completions_by_habit = {}
        if habit_ids:
            placeholders = ",".join("?" for _ in habit_ids)
            rows = db.execute(
                f"SELECT habit_id, completed_on FROM completions WHERE habit_id IN ({placeholders}) AND completed_on BETWEEN ? AND ?",
                (*habit_ids, start.isoformat(), end.isoformat()),
            ).fetchall()
            for row in rows:
                completions_by_habit.setdefault(row["habit_id"], set()).add(date.fromisoformat(row["completed_on"]))

        history_rows = [
            {"habit": habit, "dates": completions_by_habit.get(habit["id"], set())}
            for habit in habits
        ]
        return render_template("history.html", days=[end - timedelta(days=offset) for offset in range(30)], history=history_rows)

    @app.route("/settings", methods=["GET", "POST"])
    def settings():
        if request.method == "POST" and request.form.get("action") == "erase-history":
            get_db().execute("DELETE FROM completions")
            get_db().commit()
            flash("Completion history erased.", "success")
            return redirect(url_for("settings"))
        return render_template("settings.html")

    @app.post("/cookies/clear")
    def clear_cookies():
        response = redirect(url_for("index"))
        response.delete_cookie("habit_cookie_consent")
        flash("Cookie preferences cleared.", "success")
        return response

    @app.post("/cookies/accept")
    def accept_cookies():
        referrer = urlparse(request.referrer or "")
        target = (
            request.referrer
            if referrer.scheme in {"http", "https"} and referrer.netloc == request.host
            else url_for("index")
        )
        response = redirect(target)
        response.set_cookie("habit_cookie_consent", "accepted", max_age=31536000, samesite="Lax")
        return response

    return app


app = create_app()
