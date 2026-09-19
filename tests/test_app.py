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