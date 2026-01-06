from __future__ import annotations

import logging
import smtplib
import socket
import time
from email.message import EmailMessage
from typing import Optional, Tuple, List

from app.core.email_settings import EmailSettings


def _log(
    logger: logging.Logger,
    level: int,
    message: str,
    *,
    request_id: str | None,
    extra: dict | None = None,
):
    payload = extra.copy() if extra else {}
    if request_id:
        payload["request_id"] = request_id
    logger.log(level, message, extra=payload)


def smtp_ping(
    email_settings: EmailSettings,
    *,
    timeout: float = 5.0,
    logger: logging.Logger | None = None,
    request_id: str | None = None,
) -> tuple[bool, list[str], str | None]:
    """
    Prüft DNS-Auflösung und TCP-Port-Erreichbarkeit.
    """
    if not email_settings.host or not email_settings.port or not email_settings.from_email:
        return False, [], "SMTP Konfiguration fehlt (Host/Port/From sind erforderlich)"

    resolved_ips: list[str] = []
    try:
        addr_info = socket.getaddrinfo(email_settings.host, email_settings.port, proto=socket.IPPROTO_TCP)
        resolved_ips = sorted({info[4][0] for info in addr_info})
    except socket.gaierror as exc:
        if logger:
            _log(
                logger,
                logging.WARNING,
                f"DNS Lookup fehlgeschlagen für {email_settings.host} ({exc})",
                request_id=request_id,
                extra={"smtp_host": email_settings.host, "smtp_port": email_settings.port},
            )
        return False, resolved_ips, f"DNS Lookup fehlgeschlagen für {email_settings.host}"
    except Exception as exc:  # noqa: BLE001
        if logger:
            _log(
                logger,
                logging.WARNING,
                f"Auflösung für {email_settings.host} fehlgeschlagen: {exc}",
                request_id=request_id,
                extra={"smtp_host": email_settings.host, "smtp_port": email_settings.port},
            )
        return False, resolved_ips, f"Auflösung für {email_settings.host} fehlgeschlagen: {exc}"

    try:
        with socket.create_connection((email_settings.host, email_settings.port), timeout=timeout):
            pass
    except socket.timeout:
        message = f"Timeout beim Verbindungsaufbau zu {email_settings.host}:{email_settings.port}"
        if logger:
            _log(
                logger,
                logging.WARNING,
                message,
                request_id=request_id,
                extra={"smtp_host": email_settings.host, "smtp_port": email_settings.port, "resolved_ips": resolved_ips},
            )
        return False, resolved_ips, message
    except OSError as exc:
        message = f"Verbindungsaufbau zu {email_settings.host}:{email_settings.port} fehlgeschlagen ({exc})"
        if logger:
            _log(
                logger,
                logging.WARNING,
                message,
                request_id=request_id,
                extra={"smtp_host": email_settings.host, "smtp_port": email_settings.port, "resolved_ips": resolved_ips},
            )
        return False, resolved_ips, message

    return True, resolved_ips, None


def send_email(
    *,
    email_settings: EmailSettings,
    recipient: str,
    subject: str,
    body: str,
    request_id: str | None = None,
    actor: str | None = None,
    logger: logging.Logger | None = None,
) -> tuple[bool, str | None, list[str]]:
    """
    Send a plain-text email using the provided settings.
    Returns (ok, error, resolved_ips).
    """
    ok, resolved_ips, ping_error = smtp_ping(email_settings, logger=logger, request_id=request_id)
    if not ok:
        return False, ping_error, resolved_ips

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = email_settings.from_email
    message["To"] = recipient
    message.set_content(body)

    log_extra = {
        "smtp_host": email_settings.host,
        "smtp_port": email_settings.port,
        "resolved_ips": resolved_ips,
        "use_tls": email_settings.use_tls,
    }
    if actor:
        log_extra["actor"] = actor

    try:
        connect_start = time.perf_counter()
        with smtplib.SMTP(email_settings.host, email_settings.port, timeout=10) as smtp:
            connect_duration = (time.perf_counter() - connect_start) * 1000
            if logger:
                _log(
                    logger,
                    logging.DEBUG,
                    f"SMTP connected in {connect_duration:.1f}ms",
                    request_id=request_id,
                    extra=log_extra,
                )
            if email_settings.use_tls:
                tls_start = time.perf_counter()
                smtp.starttls()
                tls_duration = (time.perf_counter() - tls_start) * 1000
                if logger:
                    _log(
                        logger,
                        logging.DEBUG,
                        f"SMTP starttls in {tls_duration:.1f}ms",
                        request_id=request_id,
                        extra=log_extra,
                    )
            if email_settings.user and email_settings.password:
                auth_start = time.perf_counter()
                smtp.login(email_settings.user, email_settings.password)
                auth_duration = (time.perf_counter() - auth_start) * 1000
                if logger:
                    _log(
                        logger,
                        logging.DEBUG,
                        f"SMTP auth in {auth_duration:.1f}ms",
                        request_id=request_id,
                        extra=log_extra,
                    )
            send_start = time.perf_counter()
            smtp.send_message(message)
            send_duration = (time.perf_counter() - send_start) * 1000
            if logger:
                _log(
                    logger,
                    logging.INFO,
                    f"SMTP send ok in {send_duration:.1f}ms",
                    request_id=request_id,
                    extra=log_extra,
                )
        return True, None, resolved_ips
    except smtplib.SMTPAuthenticationError as exc:  # noqa: BLE001
        if logger:
            _log(
                logger,
                logging.ERROR,
                f"SMTP Auth fehlgeschlagen: {exc}",
                request_id=request_id,
                extra=log_extra,
            )
        return False, f"SMTP Auth fehlgeschlagen: {exc}", resolved_ips
    except smtplib.SMTPException as exc:  # noqa: BLE001
        if logger:
            _log(
                logger,
                logging.ERROR,
                f"SMTP Fehler: {exc}",
                request_id=request_id,
                extra=log_extra,
            )
        return False, f"SMTP Fehler: {exc}", resolved_ips
    except Exception as exc:  # noqa: BLE001
        if logger:
            _log(
                logger,
                logging.ERROR,
                f"E-Mail Versand fehlgeschlagen: {exc}",
                request_id=request_id,
                extra=log_extra,
            )
        return False, f"E-Mail Versand fehlgeschlagen: {exc}", resolved_ips
