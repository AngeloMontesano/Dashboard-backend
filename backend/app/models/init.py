# app/models/__init__.py
"""
Import Aggregator für Alembic Autogenerate.

Alembic muss alle Models importieren, damit metadata vollständig ist.
"""

from app.models.tenant import Tenant  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.membership import Membership  # noqa: F401
from app.models.audit_log import AdminAuditLog  # noqa: F401
