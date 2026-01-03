from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Zentrale SQLAlchemy Base für alle Modelle.
    Alembic nutzt diese Metadata für Autogenerate und Migrationen.
    """
    pass
