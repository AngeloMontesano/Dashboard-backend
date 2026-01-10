# Technische Dokumentation – Backup-System (Admin)

## Überblick
Das Backup-System stellt Admin-Endpunkte zur Verfügung, um tenant-spezifische sowie globale Backups zu erstellen, zu listen, herunterzuladen und wiederherzustellen. Die aktuelle Implementierung speichert Backups dateibasiert (JSON + ZIP) im konfigurierbaren Storage-Pfad und pflegt einen Index der Backups.

## Architektur & Speicherung
- **Storage-Root:** konfigurierbar über `BACKUP_STORAGE_PATH` (Default: `storage/backups`).
- **Storage-Schnittstelle:** Die Implementierung nutzt aktuell ein lokales Dateisystem (`BACKUP_STORAGE_DRIVER=local`). Eine Schnittstelle ist vorbereitet, sodass alternative Backends als **mögliche Lösung** ergänzt werden können.
- **Retention (optional):**
  - `BACKUP_RETENTION_MAX_DAYS` (>= 0) löscht Backups, die älter als X Tage sind.
  - `BACKUP_RETENTION_MAX_COUNT` (>= 0) begrenzt die maximale Anzahl gespeicherter Backups.
  - Retention wird beim Lesen/Schreiben des Backup-Index angewendet.
- **Scheduler (optional):**
  - `BACKUP_SCHEDULE_ENABLED` aktiviert wiederkehrende Batch-Backups.
  - `BACKUP_SCHEDULE_INTERVAL_MINUTES` steuert das Intervall für automatische Jobs.
  - Scheduler startet einen Job nur, wenn kein aktiver Job (queued/running) existiert.
  - `BACKUP_SCHEDULE_MODE=app` startet den Scheduler im API-Prozess, `worker` läuft über `python -m app.backup_worker`.
  - `BACKUP_SCHEDULE_LOCK_KEY` nutzt PostgreSQL Advisory Locks, damit in verteilten Deployments nur ein Worker plant.
- **Job-Retry & Observability:**
  - `BACKUP_JOB_MAX_RETRIES` steuert die maximale Retry-Anzahl pro Tenant.
  - `BACKUP_JOB_RETRY_DELAY_SECONDS` definiert die Wartezeit zwischen Retry-Versuchen.
  - Prometheus-Metriken: `backup_jobs_total`, `backup_job_retries_total`, `backup_job_duration_seconds`.
  - Optionaler Alert-Webhook: `BACKUP_ALERT_WEBHOOK_URL` (Timeout via `BACKUP_ALERT_WEBHOOK_TIMEOUT_SECONDS`).
- **Index:** `index.json` im Storage-Root, enthält `items`-Liste aller Backups.
- **Backup-Verzeichnis:** `<backup_id>/` im Storage-Root.
- **Dateien je Backup:**
  - `meta.json` (Backup-Metadaten inkl. Tabellenliste/Counts)
  - `tenant.json` oder `tenants.json`
  - `*.json` je tenant-gebundener Tabelle (Export der Daten per `tenant_id`)
  - `meta.json` enthält Checksums/Größen der exportierten JSON-Dateien zur Integritätsprüfung.
  - ZIP-Download wird on-demand aus den JSON-Dateien erzeugt.

## API-Endpunkte (Admin)
Alle Endpunkte laufen unter `/admin/backups`.

### Liste und Details
- `GET /admin/backups`
  - Query: `tenant_id`, `scope` (`tenant` | `all`)
  - Liefert `BackupListResponse`.
- `GET /admin/backups/history`
  - Query: `action`, `created_from`, `created_to`, `limit`, `offset`
  - Liefert Audit-Log-Einträge für Backups.
- `GET /admin/backups/{backup_id}`
  - Liefert `BackupEntry`.

### Erstellung
- `POST /admin/backups/tenants/{tenant_id}`
  - Erstellt ein Backup für einen Tenant und schreibt Audit-Log.
- `POST /admin/backups/all`
  - Startet einen Job für Backups aller Tenants (Batch).
  - Antwort enthält Job-Status und Job-ID.
  - Geplante Jobs setzen `trigger=scheduler` und `scheduled_at`.

### Jobs / Monitoring
- `GET /admin/backups/jobs`
  - Liefert alle Backup-Jobs inkl. Status/Progress.
- `GET /admin/backups/jobs/{job_id}`
  - Liefert Details eines Backup-Jobs.

### Download
- `GET /admin/backups/{backup_id}/download`
  - Liefert ZIP mit JSON-Dateien.
- `GET /admin/backups/{backup_id}/files/{filename}`
  - Liefert einzelne JSON-Datei aus dem Backup-Verzeichnis.

### Restore
- `POST /admin/backups/{backup_id}/restore`
  - Stellt Tenant-Daten wieder her (Upsert/Idempotenz) und prüft Counts.
  - Prüft Checksums/Größen der JSON-Dateien vor dem Import.
  - Führt Row-Level-Validierung (Tenant-ID, PK-Felder) und FK-Checks innerhalb des Backups aus.
  - Markiert Backup als restored, schreibt Audit-Log.
  - Unterstützt aktuell nur Tenant-Backups.

## Datenmodelle (Kurz)
- **BackupEntry**: `id`, `scope`, `tenant_id`, `tenant_slug`, `created_at`, `status`, `restored_at`, `files`.
- **BackupFileInfo**: `name`, `size_bytes`, `size_label`.

## Audit-Log
Bei `backup.create` und `backup.restore` werden Audit-Log-Einträge geschrieben. Der Actor wird aus `x-admin-actor` gelesen (Fallback `system`).

## Status & Limitierungen (Stand heute)
- **Export:** Tenant-gebundene Tabellen werden per DB-Introspektion exportiert.
- **Restore:** Datenimport via Upsert/Idempotenz (FK-Reihenfolge aus Metadata).
- **Job-Queue:** `POST /admin/backups/all` erzeugt einen Job und verarbeitet Tenants sequenziell.
- **Scheduler:** Optionaler Worker erzeugt wiederkehrende Batch-Jobs (in-process).
  - Für verteilte Deployments: dedizierten Worker-Prozess starten und `BACKUP_SCHEDULE_MODE=worker` im API setzen.
- **Storage-Interface vorhanden:** Aktuell nur lokale Implementierung angebunden (Driver = `local`).
- **Checksums:** Metadaten enthalten Checksums und werden beim Restore validiert.
- **Integritätschecks:** Restore prüft Tenant-ID/PKs pro Zeile sowie einfache FK-Beziehungen innerhalb des Backups.
- **Erweiterte Checks:** Composite-FKs innerhalb des Backups und referenzielle Checks gegen Live-DB.
- **Alerting:** Bei Job-Fehlern oder Teilfehlern wird optional ein Webhook ausgelöst.
- **Admin-UI:** Backup-Liste, Monitoring und Job-Übersicht nutzen echte Admin-API Daten (keine Demo-Daten).
- **Audit-UI:** Historie-Tabelle mit Filter nach Aktion/Zeitraum nutzt `/admin/backups/history`.
- **Polling:** UI aktualisiert laufende Jobs periodisch, bis keine Jobs mehr im Status `queued`/`running` sind.

## Empfehlungen für nächste Ausbaustufe
1. **Storage-Abstraktion** als mögliche Lösung (z. B. Provider-Interface für alternative Backends).
2. **Validierung**: erweiterte Checks (z. B. zusammengesetzte FKs oder referenzielle Checks gegen Live-DB).
3. **Job-Observability**: Retry-Strategien, Alerting und Metriken für fehlgeschlagene Jobs.
