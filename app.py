from habit_tracker.app import app, create_app

__all__ = ["app", "create_app"]


if __name__ == "__main__":
    app.run(debug=True)
