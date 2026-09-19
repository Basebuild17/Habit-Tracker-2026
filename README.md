# Habit Tracker

A small web app for tracking daily habits and streaks, built with Flask and SQLite.

<!-- Add a screenshot here once the app is ready: ![Screenshot](docs/screenshot.png) -->

## Features

- Add and delete habits
- Add up to three tags to each habit
- Customize a habit's active weekdays
- Edit and reorder habits
- Check a habit off for today
- See the current streak for each habit
- See daily completion progress and a celebration animation
- View weekly statistics and a 30-day completion calendar
- Accept or erase the app's preference cookie
- Save completion history automatically or erase it from Settings

## Run It Locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app run --debug
```

Then open <http://127.0.0.1:5000>.

## Run the Tests

```bash
pytest
```

## How It Works

- `app.py` holds the routes and form handlers
- `db.py` and `schema.sql` set up SQLite
- `streaks.py` holds the streak and weekly statistics logic
- `templates/` and `static/` hold the HTML and CSS
- `tests/` contains automated tests

Completion history is stored locally in SQLite. The Settings page can erase all completion records while keeping the habit definitions.

## What I Would Improve Next

- Add habit reminders
- Add charts for longer-term progress
- Add user accounts if the app needs multi-user support

## Hosting Note

Some free hosting services wipe the filesystem during redeploys. Do not rely on a local SQLite file as the only copy of important data; use persistent storage or backups before deploying.
