FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/Basebuild17/Habit-Tracker-2026"
LABEL org.opencontainers.image.title="Habit Tracker"
LABEL org.opencontainers.image.description="A web app for tracking daily habits"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

RUN mkdir -p /data

EXPOSE 5000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} app:app"]
name: Publish Docker image

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

permissions:
  contents: read
  packages: write

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/Basebuild17/Habit-Tracker-2026

      - name: Build and push Docker image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/Basebuild17/Habit-Tracker-2026:latest
            ghcr.io/Basebuild17/Habit-Tracker-2026:${{ github.sha }}
          labels: ${{ steps.meta.outputs.labels }}
context: .
labels:
  - org.opencontainers.image.created=2026-10-24T21:06:08.297Z
  - org.opencontainers.image.description=Break or create a new habit in 30 days
  - org.opencontainers.image.licenses=GPL-3.0
  - org.opencontainers.image.revision=e0857caab61a58b7d017816a031e37d17e932123
  - org.opencontainers.image.source=https://github.com/Basebuild17/Habit-Tracker-2026
  - org.opencontainers.image.title=Habit-Tracker-2026
  - org.opencontainers.image.url=https://github.com/Basebuild17/Habit-Tracker-2026
  - org.opencontainers.image.version=v.1.0.0.0
push: true
tags:
  - ghcr.io/basebuild17/habit-tracker-2026:v.1.0.0.0
  - ghcr.io/basebuild17/habit-tracker-2026:latest
