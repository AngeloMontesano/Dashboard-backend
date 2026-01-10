# Anwenderdokumentation – Backups im Admin-UI

## Zweck
Mit dem Admin-Backup-Bereich können Administratoren Backups pro Tenant oder für alle Tenants erstellen, die Backup-Historie einsehen und vorhandene Backups herunterladen oder wiederherstellen.

## Voraussetzungen
- Admin-Zugriff auf das System.
- Das Backend ist erreichbar.
- `BACKUP_STORAGE_PATH` ist korrekt gesetzt (Server-seitig).
- Optional: `BACKUP_STORAGE_DRIVER=local` (Standard) ist konfiguriert.
- Optional: Retention-Parameter (`BACKUP_RETENTION_MAX_DAYS`, `BACKUP_RETENTION_MAX_COUNT`, jeweils >= 0) sind konfiguriert.

## Funktionen im Überblick

### 1) Backup-Liste
- Anzeige aller vorhandenen Backups.
- Filter nach **Tenant** und **Scope** (Tenant/Alle).
- Anzeige von Erstellzeit, Status, Dateien.
- Metadaten enthalten Checksums/Größen zur Integritätsprüfung (technisch).

### 2) Historie / Audit
- Zeigt Audit-Log-Einträge für Backup-Erstellung und Restore.
- Ermöglicht Nachvollziehbarkeit von Änderungen.

### 3) Backup erstellen
- **Tenant-Backup**: erstellt ein Backup für einen ausgewählten Tenant.
- **Backup für alle Tenants**: startet einen Job, der Backups für alle Tenants erstellt.

### 4) Jobs / Monitoring
- Jobs zeigen den Fortschritt von Batch-Backups (Status, Anzahl bearbeiteter Tenants).

### 5) Download
- **ZIP-Download**: lädt alle JSON-Dateien des Backups als ZIP.
- **Einzeldatei-Download**: lädt eine einzelne JSON-Datei aus dem Backup.

### 6) Restore
- Startet die Wiederherstellung für ein ausgewähltes Backup.
- Es wird ein Audit-Log-Eintrag erstellt.
- Restore spielt Tenant-Daten per Upsert wieder ein (idempotent).
- Checksums/Größen werden vor dem Import automatisch geprüft.
- Restore ist aktuell nur für Tenant-Backups verfügbar.

## Aktueller Funktionsumfang (Wichtig)
- Backups enthalten tenant-gebundene Tabellen als JSON-Exporte.
- Restore importiert die Daten idempotent (Upsert) und prüft Tabellen-Counts.

## Best Practices
- Verwende den ZIP-Download als Sicherungskopie.
- Prüfe die Backup-Liste regelmäßig.
- Beachte mögliche automatische Aufräumregeln (Retention).
- Nutze Restore nur, wenn die Auswirkungen bekannt sind (es werden echte Daten überschrieben).

## Fehlersuche
- **Backup nicht in Liste:** Seite neu laden, Filter prüfen.
- **Download schlägt fehl:** Backup-ID oder Datei nicht vorhanden.
- **Restore fehlgeschlagen:** Prüfe Admin-Zugriff und Audit-Logs.

## Was als Nächstes kommt
- Erweiterbare Storage-Schnittstelle als mögliche Lösung (alternative Backends).
- Optional: wiederkehrende Zeitplanung für Job-Queue.
- Zusätzliche Integritätsprüfungen (z. B. referenzielle Checks).
