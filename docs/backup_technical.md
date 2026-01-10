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
- **Storage-Interface vorhanden:** Aktuell nur lokale Implementierung angebunden (Driver = `local`).
- **Checksums:** Metadaten enthalten Checksums und werden beim Restore validiert.
- **Integritätschecks:** Restore prüft Tenant-ID/PKs pro Zeile sowie einfache FK-Beziehungen innerhalb des Backups.

## Empfehlungen für nächste Ausbaustufe
1. **Scheduler**: Persistenter Worker/Planner (z. B. Cron/Scheduler) für verteilte Deployments.
2. **Storage-Abstraktion** als mögliche Lösung (z. B. Provider-Interface für alternative Backends).
3. **Validierung**: erweiterte Checks (z. B. zusammengesetzte FKs oder referenzielle Checks gegen Live-DB).
