#!/bin/sh
set -e

echo "Run migrations..."
alembic upgrade heads

echo "Seed initial data (only if empty)..."
python -m app.scripts.seed_initial

echo "Start API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
