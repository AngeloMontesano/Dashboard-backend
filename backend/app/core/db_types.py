from __future__ import annotations

import uuid

from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql import CITEXT, JSONB, UUID
from sqlalchemy.types import TypeDecorator


class GUID(TypeDecorator):
    """
    Cross-database UUID Unterstützung.
    - PostgreSQL: nutzt native UUID Spalte
    - Andere Dialekte (z. B. SQLite): speichert als 36 Zeichen String
    """

    impl = UUID
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


class CIText(TypeDecorator):
    """
    Case-insensitive Text.
    - PostgreSQL: CITEXT
    - Andere Dialekte: String mit NOCASE Collation
    """

    impl = String
    cache_ok = True

    def __init__(self, length: int = 255, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.length = length

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(CITEXT())
        return dialect.type_descriptor(String(self.length, collation="NOCASE"))


class JSONBType(TypeDecorator):
    """
    JSON Kompatibilität.
    - PostgreSQL: JSONB
    - Andere Dialekte: generisches JSON
    """

    impl = JSONB
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB)
        return dialect.type_descriptor(JSON)
