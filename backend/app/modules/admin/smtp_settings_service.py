from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = DATA_DIR / "smtp_settings.json"


@dataclass
class SmtpConfig:
    host: str
    port: int
    from_email: str
    user: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True


def _load_raw() -> dict:
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text())
        except Exception:
            return {}
    return {}


def load_smtp_settings() -> Optional[SmtpConfig]:
    raw = _load_raw()
    if not raw:
        return None
    try:
        return SmtpConfig(
            host=raw.get("host") or "",
            port=int(raw.get("port") or 0),
            from_email=raw.get("from_email") or "",
            user=raw.get("user") or None,
            password=raw.get("password") or None,
            use_tls=bool(raw.get("use_tls", True)),
        )
    except Exception:
        return None


def save_smtp_settings(payload: dict) -> SmtpConfig:
    """
    Persistiert SMTP Settings in eine JSON Datei.
    Passwort wird nur überschrieben, wenn übergeben.
    """
    current = load_smtp_settings() or SmtpConfig(
        host="",
        port=0,
        from_email="",
        user=None,
        password=None,
        use_tls=True,
    )
    merged = {
        "host": payload.get("host", current.host),
        "port": int(payload.get("port", current.port or 0)),
        "from_email": payload.get("from_email", current.from_email),
        "user": payload.get("user", current.user),
        "password": payload.get("password", current.password),
        "use_tls": payload.get("use_tls", current.use_tls),
    }
    SETTINGS_FILE.write_text(json.dumps(merged, indent=2))
    return SmtpConfig(
        host=merged["host"] or "",
        port=int(merged["port"] or 0),
        from_email=merged["from_email"] or "",
        user=merged.get("user") or None,
        password=merged.get("password") or None,
        use_tls=bool(merged.get("use_tls", True)),
    )


def get_active_smtp_settings() -> Optional[SmtpConfig]:
    """
    Liest gespeicherte SMTP Settings aus Datei.
    """
    stored = load_smtp_settings()
    if stored and stored.host and stored.port and stored.from_email:
        return stored
    return None
