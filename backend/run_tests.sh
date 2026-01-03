#!/bin/sh
set -eu

echo "Run migrations on test DB"
alembic upgrade head

echo "Run pytest"
python -m pytest -q --disable-warnings



