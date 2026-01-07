## Done (Recent)
- [ADMIN-UI-01] (ADMIN_UI_STYLE_SYSTEM) Admin-Styles modularisieren (tokens/base/layout/utilities/components), View-Styles auslagern und Utilities dokumentieren.
- [ADMIN-UI-02] (ADMIN_UI_STYLE_SYSTEM) Theme-Handling zentralisieren (`src/theme/theme.ts`) und useTheme darauf aufbauen.
- [ADMIN-UI-03] (ADMIN_UI_STYLE_SYSTEM) Layout-Politur für Filter-/Action-Reihen und Import-File-Inputs (Grid/Spacing, responsive).
- [ADMIN-UI-04] (ADMIN_UI_STYLE_SYSTEM) Admin-Standards dokumentieren (`docs/standards/ADMIN_UI_STANDARDS.md`) + WORKLOG/TODO pflegen.

## Now (Top 10)
- [A-01] Tenant-Status-API spezifizieren (`/api/public/tenant-status`) – Epic A
- [A-04] Customer-Bootstrap prüft Tenant-Status vor Router-Init – Epic A
- [B-01] Datenmodell-Entwurf globale Kataloge (Tabellen/Keys) – Epic B
- [C-02] UX-Flow Reporting Startseite mit Top-5 Default skizzieren – Epic C
- [D-01] Ziel-Routen + Prefill-Filter für KPI-Karten festlegen – Epic D
- [E-02] UI-Spezifikation für neuen Bestell-Dialog (Tabellen-Layout) – Epic E
- [F-03] UX-Flow Offline-Queue Liste + Detail (Tabs/Badges) beschreiben – Epic F
- [G-01] Doku-Struktur (technisch + User) definieren – Epic G
- [H-01] Optionen für leichtes Monitoring ohne Grafana evaluieren – Epic H
- [I-01] Felddefinitionen für globale/tenant-spezifische Kontakte dokumentieren – Epic I

### Parallelisierungs-Empfehlung (Now)
- Stream 1 (Backend/Docs): A-01 (Status-API Spezifikation) + B-01 (Globales Datenmodell) + H-01 (Monitoring-Optionen) parallel abstimmen.
- Stream 2 (Customer UX): A-04 (Bootstrap Preflight) + C-02 (Reporting UX-Flow) + D-01 (KPI-Routen) in einem UX-Review-Slot bündeln.
- Stream 3 (Admin/Docs): G-01 (Doku-Struktur) + I-01 (Kontakt-Felder) gemeinsam erarbeiten; Wechselwirkungen in Admin-Settings klären.

#### Deliverables je Stream (Now)
- Stream 1: Draft `docs/openapi/` Ergänzungen für A-01 (`TENANT_STATUS.md`), Datenmodell-Skizze für B-01, Kurzvergleich Monitoring-Optionen (H-01) als Markdown-Notiz.
- Stream 2: Low-fi Wireframes (A-04, C-02, D-01) und Navigation/Prefill-Flows als Diagramm/Markdown.
- Stream 3: Informationsarchitektur der Doku (G-01) + Felddefinitionen/Abschnitte für Kontakte (I-01) als Übersichtstabelle.

### Parallelisierungs-Empfehlung (Next/Later)
- Stream 1: A-05/A-10 (Tenant-Status UX/QA), B-02 (Admin-API Spezifikation) – gleiche Review-Runde nutzen.
- Stream 2: C-03/C-04 (Reporting Komponenten), D-02 (Router-Interface Prefill) – gemeinsam definieren und stubben.
- Stream 3: E-03/E-04/E-05 (Order-Dialog Konzept/Validierung), F-04/F-05 (Queue-Komponenten/Retry) – geteilte Guidelines für UX/Fehlertexte anwenden.

## Next
- [A-05] Tenant-Status-View Texte/CTAs finalisieren – Epic A
- [A-10] QA-Checkliste Tenant-Status (404/Headers/Mobile/Darkmode) – Epic A
- [B-02] Admin-API Spezifikation globale Kategorien/Typen/Branchen – Epic B
- [C-03] Live-Suche-Komponente Reporting entwerfen (Prefix/Debounce) – Epic C
- [D-02] Router-Interface für Prefill dokumentieren – Epic D
- [E-03] Dialog-Komponente Mehrfachzeilen planen – Epic E
- [F-04] Komponentenstruktur Queue (Liste/Detail/Aktionen) planen – Epic F
- [G-05] Help-Button-Konzept Customer festlegen – Epic G
- [H-04] Docker-Compose-Snippet für Monitoring-Light dokumentieren – Epic H
- [I-04] Admin-UI Formulare globale Kontakte entwerfen – Epic I

## Later
- [A-08] Status-Caching/Retry-Strategie implementieren (Konzept) – Epic A
- [A-11] Proxy/404 Smoke-Test-Plan erstellen – Epic A
- [B-10] Konzept Verteilung globaler Kataloge an Tenants dokumentieren – Epic B
- [C-09] Export-Konzept (Button/Format) festlegen – Epic C
- [D-08] QA-Checkliste Navigation KPI-Karten – Epic D
- [E-07] Storno-Konzept dokumentieren – Epic E
- [F-08] QA-Checkliste Offline-Queue – Epic F
- [G-06] Help/Debug-Bereich Admin planen – Epic G
- [H-07] QA/Smoke-Plan Statusseite – Epic H
- [I-08] QA-Checkliste Kontakte (Validierung/Fallback) – Epic I
