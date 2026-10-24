from datetime import date, timedelta
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from db import close_db, get_db, init_db
from streaks import current_streak_for_schedule, history_for_habit, weekly_completion


WEEKDAYS = [(0, "Mon"), (1, "Tue"), (2, "Wed"), (3, "Thu"), (4, "Fri"), (5, "Sat"), (6, "Sun")]


def habit_form_values(form):
    tags = [form.get(f"tag{index}", "").strip()[:24] for index in range(1, 4)]
    frequency = sorted({int(day) for day in form.getlist("frequency") if day.isdigit() and 0 <= int(day) <= 6})
    tracking_type = form.get("tracking_type", "boolean") if form.get("tracking_type") in {"boolean", "metric"} else "boolean"
    try:
        target_value = max(float(form.get("target_value", 1)), 1)
    except ValueError:
        target_value = 1
    return tags, ",".join(str(day) for day in frequency) or "0,1,2,3,4,5,6", tracking_type, target_value, form.get("unit", "").strip()[:16], form.get("category", "Health"), form.get("color", "#2d7a52")


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=Path(app.instance_path) / "habits.sqlite",
    )

    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    @app.get("/")
    def index():
        today = date.today().isoformat()
        habits = get_db().execute(
            """
            SELECT h.id, h.name,
                     EXISTS (
                       SELECT 1 FROM completions c
                       WHERE c.habit_id = h.id AND c.completed_on = ?
                                     ) AS completed_today, h.tag1, h.tag2, h.tag3, h.frequency,
                                     h.tracking_type, h.target_value, h.unit, h.category, h.color, h.archived
            FROM habits h
                                 WHERE h.archived = 0
                                 ORDER BY h.position, h.id
            """,
            (today,),
        ).fetchall()
        habit_cards = [
            {
                "id": habit["id"],
                "name": habit["name"],
                "completed_today": bool(habit["completed_today"]),
                "streak": current_streak_for_schedule(habit["id"], habit["frequency"]),
                "tags": [tag for tag in (habit["tag1"], habit["tag2"], habit["tag3"]) if tag],
                "frequency": {int(day) for day in habit["frequency"].split(",") if day},
                "tracking_type": habit["tracking_type"],
                "target_value": habit["target_value"],
                "unit": habit["unit"] or "",
                "category": habit["category"],
                "color": habit["color"],
            }
            for habit in habits
        ]
        return render_template(
            "index.html",
            habits=habit_cards,
            today=date.today().strftime("%A, %B %-d"),
            weekdays=WEEKDAYS,
            completed_count=sum(habit["completed_today"] for habit in habit_cards),
        )

    @app.post("/habits")
    def add_habit():
        name = request.form.get("name", "").strip()
        tags, frequency, tracking_type, target_value, unit, category, color = habit_form_values(request.form)
        if not name:
            flash("Give your habit a name first.", "error")
        elif len(name) > 80:
            flash("Habit names must be 80 characters or fewer.", "error")
        else:
            db = get_db()
            position = db.execute("SELECT COALESCE(MAX(position), -1) + 1 FROM habits").fetchone()[0]
            db.execute(
                "INSERT INTO habits (name, tag1, tag2, tag3, frequency, tracking_type, target_value, unit, category, color, position) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (name, *tags, frequency, tracking_type, target_value, unit, category, color, position),
            )
            db.commit()
            flash(f'Added "{name}".', "success")
        return redirect(url_for("index"))

    @app.post("/habits/<int:habit_id>/toggle")
    def toggle_habit(habit_id):
        db = get_db()
        habit = db.execute("SELECT name, tracking_type, target_value FROM habits WHERE id = ?", (habit_id,)).fetchone()
        if habit is None:
            flash("That habit no longer exists.", "error")
            return redirect(url_for("index"))

        today = date.today().isoformat()
        try:
            value = max(float(request.form.get("value", habit["target_value"])), 0)
        except ValueError:
            value = habit["target_value"]
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
                "INSERT INTO completions (habit_id, completed_on, value, note) VALUES (?, ?, ?, ?)",
                (habit_id, today, value, request.form.get("note", "").strip()[:500]),
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
            tags, frequency, tracking_type, target_value, unit, category, color = habit_form_values(request.form)
            if not name or len(name) > 80:
                flash("Use a habit name between 1 and 80 characters.", "error")
            else:
                db.execute(
                    "UPDATE habits SET name = ?, tag1 = ?, tag2 = ?, tag3 = ?, frequency = ?, tracking_type = ?, target_value = ?, unit = ?, category = ?, color = ? WHERE id = ?",
                    (name, *tags, frequency, tracking_type, target_value, unit, category, color, habit_id),
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

    @app.post("/habits/<int:habit_id>/archive")
    def archive_habit(habit_id):
        get_db().execute("UPDATE habits SET archived = 1 WHERE id = ?", (habit_id,))
        get_db().commit()
        flash("Habit archived.", "success")
        return redirect(url_for("index"))

    @app.post("/habits/<int:habit_id>/restore")
    def restore_habit(habit_id):
        get_db().execute("UPDATE habits SET archived = 0 WHERE id = ?", (habit_id,))
        get_db().commit()
        return redirect(url_for("archive"))

    @app.get("/archive")
    def archive():
        habits = get_db().execute("SELECT * FROM habits WHERE archived = 1 ORDER BY position, id").fetchall()
        return render_template("archive.html", habits=habits)

    @app.get("/stats")
    def stats():
        end = date.today()
        start = end - timedelta(days=6)
        rows = weekly_completion(start, end)
        total = sum(row["completed"] for row in rows)
        habit_count = get_db().execute("SELECT COUNT(*) FROM habits").fetchone()[0]
        return render_template(
            "stats.html",
            days=rows,
            total=total,
            possible=len(rows) * habit_count,
        )

    @app.get("/history")
    def history():
        end = date.today()
        start = end - timedelta(days=29)
        habits = get_db().execute("SELECT id, name, tag1, tag2, tag3 FROM habits ORDER BY position, id").fetchall()
        history = [
            {"habit": habit, "dates": history_for_habit(habit["id"], start, end)}
            for habit in habits
        ]
        return render_template("history.html", days=[end - timedelta(days=offset) for offset in range(30)], history=history)

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
        response = redirect(request.referrer or url_for("index"))
        response.set_cookie("habit_cookie_consent", "accepted", max_age=31536000, samesite="Lax")
        return response

    return app


app = create_app()