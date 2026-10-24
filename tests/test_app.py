import sqlite3

from app import create_app


def test_add_and_complete_habit(client):
    response = client.post("/habits", data={"name": "Drink water"}, follow_redirects=True)
    assert b"Drink water" in response.data

    response = client.post("/habits/1/toggle", follow_redirects=True)
    assert b"1 day streak" in response.data


def test_blank_habit_is_rejected(client):
    response = client.post("/habits", data={"name": "   "}, follow_redirects=True)
    assert b"Give your habit a name first" in response.data


def test_delete_habit(client):
    client.post("/habits", data={"name": "Journal"}, follow_redirects=True)
    response = client.post("/habits/1/delete", follow_redirects=True)
    assert b"Journal" not in response.data


def test_habit_tags_frequency_and_edit(client, app):
    client.post(
        "/habits",
        data={"name": "Walk", "tag1": "Health", "tag2": "Outside", "tag3": "Morning", "frequency": ["0", "2"]},
    )
    response = client.get("/")
    assert b"Health" in response.data
    assert b"Outside" in response.data

    client.post(
        "/habits/1/edit",
        data={"name": "Evening walk", "tag1": "Movement", "frequency": ["4"]},
    )
    with app.app_context():
        from db import get_db

        habit = get_db().execute("SELECT * FROM habits WHERE id = 1").fetchone()
        assert habit["name"] == "Evening walk"
        assert habit["tag1"] == "Movement"
        assert habit["frequency"] == "4"


def test_history_and_erase_history(client, app):
    client.post("/habits", data={"name": "Read"})
    client.post("/habits/1/toggle")
    response = client.get("/history")
    assert response.status_code == 200
    assert b"Read" in response.data
    client.post("/settings", data={"action": "erase-history"})
    with app.app_context():
        from db import get_db

        assert get_db().execute("SELECT COUNT(*) FROM completions").fetchone()[0] == 0


def test_cookie_accept_sets_preference(client):
    response = client.post("/cookies/accept")
    assert response.status_code == 302
    assert "habit_cookie_consent=accepted" in response.headers["Set-Cookie"]


def test_metric_habit_can_be_archived_and_restored(client, app):
    client.post(
        "/habits",
        data={
            "name": "Drink water",
            "tracking_type": "metric",
            "target_value": "8",
            "unit": "glasses",
            "category": "Health",
            "color": "#10b981",
        },
    )
    response = client.get("/")
    assert b"goal 8 glasses" in response.data
    client.post("/habits/1/archive")
    assert b"Drink water" not in client.get("/").data
    assert b"Drink water" in client.get("/archive").data
    client.post("/habits/1/restore")
    assert b"Drink water" in client.get("/").data


def test_completion_can_store_a_note(client, app):
    client.post("/habits", data={"name": "Reflect"})
    client.post("/habits/1/toggle", data={"note": "Felt focused"})
    with app.app_context():
        from db import get_db

        completion = get_db().execute("SELECT note FROM completions").fetchone()
        assert completion["note"] == "Felt focused"
def test_cookie_accept_does_not_redirect_to_external_referrer(client):
    response = client.post(
        "/cookies/accept",
        headers={"Referer": "https://example.com/untrusted"},
    )

    assert response.headers["Location"] == "/"


def test_reorder_is_preserved_after_database_reinitialization(client, app):
    client.post("/habits", data={"name": "First"})
    client.post("/habits", data={"name": "Second"})
    client.post("/habits/2/move/up")

    create_app({
        "TESTING": True,
        "SECRET_KEY": "test",
        "DATABASE": app.config["DATABASE"],
    })
    response = client.get("/")

    assert response.data.index(b"<h3>Second</h3>") < response.data.index(b"<h3>First</h3>")


def test_weekly_possible_count_uses_habit_schedule(client):
    client.post("/habits", data={"name": "Monday habit", "frequency": ["0"]})
    client.post("/habits", data={"name": "Thursday habit", "frequency": ["3"]})

    response = client.get("/stats")

    assert b"2 possible" in response.data


def test_legacy_habits_get_initial_positions(tmp_path):
    database_path = tmp_path / "legacy.sqlite"
    database = sqlite3.connect(database_path)
    database.execute("CREATE TABLE habits (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
    database.executemany(
        "INSERT INTO habits (id, name) VALUES (?, ?)",
        [(4, "Older"), (9, "Newer")],
    )
    database.commit()
    database.close()

    app = create_app({"TESTING": True, "DATABASE": database_path})

    with app.app_context():
        from db import get_db

        positions = get_db().execute(
            "SELECT id, position FROM habits ORDER BY id"
        ).fetchall()

    assert [(row["id"], row["position"]) for row in positions] == [(4, 4), (9, 9)]


def test_app_uses_configured_secret_key(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "private-test-key")

    app = create_app({"TESTING": True, "DATABASE": tmp_path / "configured.sqlite"})

    assert app.config["SECRET_KEY"] == "private-test-key"
