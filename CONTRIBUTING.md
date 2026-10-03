# Contributing

Thanks for helping improve Habit Tracker! Small, focused pull requests are
especially welcome.

## Set up the project

1. Install Python 3.11 or newer.
2. Create and activate a virtual environment, then install the requirements:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

   On Windows, use `py -m venv .venv` and `.venv\Scripts\activate`.
3. Start the app with `flask --app app run --debug`.
4. Run the test suite with `python -m pytest`.

The app creates its SQLite database under Flask's instance directory. Tests use
a temporary database and do not modify your local data.

## Before opening a pull request

- Check existing issues before starting a substantial change; for a new feature,
  open an issue first to agree on scope.
- Keep each change focused and add or update tests for behavior changes.
- Run `python -m pytest` and include the result in your pull request.
- Update the README or other documentation when setup or user-facing behavior
  changes.
- Explain the problem solved and any trade-offs in the pull request description.

## Suggested Hacktoberfest contributions

These are ideas, not a committed roadmap. Please open an issue before beginning
a larger change.

| Priority | Idea | Size |
| --- | --- | --- |
| 1 | Make the 30-day history calendar easier to use with assistive technology (for example, add date-aware accessible labels and test the rendered markup). | Good first issue |
| 2 | Add an option to export completion history as CSV, with tests for empty history and correctly escaped values. | Intermediate |
| 3 | Add a tag filter to the history view, preserving the current unfiltered view and testing combinations of tags. | Intermediate |

Longer-term, reminders or multi-user accounts would need product and deployment
decisions; discuss those in an issue before proposing implementation.
