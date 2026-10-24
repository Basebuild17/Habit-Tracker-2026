FROM python:3.12-slim

LABEL org.opencontainers.image.title="Habit Tracker"
LABEL org.opencontainers.image.description="A web app for tracking daily habits"
LABEL org.opencontainers.image.source="https://github.com/YOUR-USERNAME/habit-tracker"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
