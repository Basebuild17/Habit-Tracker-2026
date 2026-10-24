# Habit Tracker

A small Flask web app for tracking daily habits and streaks.

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

## Installation

Create and activate a virtual environment, then install the package in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

On Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Run the app

You can start the app using the package entry point or the module runner:

```bash
habit-tracker
```

or:

```bash
python -m habit_tracker
```

Then open http://127.0.0.1:5000 in your browser.

## Environment variables

For local development, the app will use a default demo secret key if `SECRET_KEY` is not set. For a private deployment, set a stronger value:

```bash
export SECRET_KEY="your-strong-secret-key"
```

## Run the tests

```bash
python -m pytest
```

## Project structure

- `habit_tracker/` contains the packaged Flask app
- `templates/` contains the HTML templates
- `static/` contains styling assets
- `schema.sql` defines the SQLite schema
- `tests/` contains automated tests

## How it works

- `habit_tracker/app.py` holds the routes and form handlers
- `habit_tracker/db.py` and `schema.sql` set up SQLite
- `habit_tracker/streaks.py` holds the streak and weekly statistics logic
- `templates/` and `static/` hold the HTML and CSS
- `tests/` contains automated tests

Completion history is stored locally in SQLite. The Settings page can erase all completion records while keeping the habit definitions.

## Contributing

Bug reports, focused fixes, tests, and documentation improvements are welcome.
Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, pull request guidance, and beginner-friendly project ideas.

## Hosting note

This is a local, single-user app and is not designed for public multi-user hosting. Some free hosting services wipe their filesystem during redeploys. If you deploy a private instance, set a strong `SECRET_KEY` environment variable, use persistent storage, and back up the SQLite database.
