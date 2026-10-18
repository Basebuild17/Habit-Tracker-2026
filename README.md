# Habit Tracker

A small web app for tracking daily habits and streaks, built with Flask and SQLite.

## Features

- Add and delete habits
- Add up to three tags to each habit
- Customize a habit's active weekdays
- Edit and reorder habits
- Check a habit off for today
- See the current streak for each habit
- See daily completion progress and a celebration animation
- View weekly statistics and a 30-day completion calendar
- Store or erase an optional cookie preference
- Save completion history automatically or erase it from Settings

## Run It Locally

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
flask --app app run --debug
```

Then open <http://127.0.0.1:5000>.
On Windows, create the environment with `py -m venv .venv` and run the Flask
command with `py -m flask --app app run --debug`.

Python 3.11 or newer is recommended.

## Run the Tests

```bash
python -m pytest
```

On Windows, activate the environment with `.venv\Scripts\activate` before
running these commands.

## How It Works

- `app.py` holds the routes and form handlers
- `db.py` and `schema.sql` set up SQLite
- `streaks.py` holds the streak and weekly statistics logic
- `templates/` and `static/` hold the HTML and CSS
- `tests/` contains automated tests

Completion history is stored locally in SQLite. The Settings page can erase all completion records while keeping the habit definitions.

## Contributing

Bug reports, focused fixes, tests, and documentation improvements are welcome.
Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, pull request guidance, and
beginner-friendly Hacktoberfest ideas.

## Hosting Note

This is a local, single-user app and is not designed for public multi-user
hosting. Some free hosting services wipe their filesystem during redeploys. If
you deploy a private instance, set a strong `SECRET_KEY` environment variable,
use persistent storage, and back up the SQLite database.
