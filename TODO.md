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

## CSS-Duplizierung (Klassifizierung A-D)
- [CSS-A1] Tokens Light/Dark (admin_frontend/admin-ui/src/styles/tokens.css:10-85 ↔ customer_frontend/customer-ui/src/styles/tokens.css:10-85) – **A (identisch, redundant)**. Source of Truth: docs/standards/THEME_TOKENS.md + customer_frontend/customer-ui/src/styles/tokens.css. Admin-Kopie später als LEGACY markieren.
- [CSS-B1] base.css body/app Hintergründe + Textfarbe (admin_frontend/admin-ui/src/styles/base.css:12-44 ↔ customer_frontend/customer-ui/src/styles/base.css:12-44) – **B (semantisch gleich, minimale Abweichung)**. Source of Truth: Token-Mapping auf `--surface-0`/`--text-strong` in base.css; Admin nutzt noch Legacy-Aliase (`--bg`, `--text`).
- [CSS-B2] Layout Shell/Sidebar/Nav (admin_frontend/admin-ui/src/styles/layout.css:8-127 ↔ customer_frontend/customer-ui/src/styles/layout.css:8-127) – **B (semantisch gleich, minimale Abweichung)**. Source of Truth: Admin-Layout (visuelle Referenz); Customer-Varianten sollten auf dieselbe Radius/Shadow-Skala zurückgeführt werden.
- [CSS-B3] Layout Cards/Inputs/Status/Buttons (admin_frontend/admin-ui/src/styles/layout.css:231-360 ↔ customer_frontend/customer-ui/src/styles/layout.css:231-360) – **B (semantisch gleich, minimale Abweichung)**. Source of Truth: Admin-Layout für Spacing/Radius, Customer-Input-Tokens für Farb-/Focus-States.
- [CSS-B4] Utilities page/section/chip/filter (admin_frontend/admin-ui/src/styles/utilities.css:8-122 ↔ customer_frontend/customer-ui/src/styles/utilities.css:8-122) – **B (semantisch gleich, minimale Abweichung)**. Source of Truth: Admin-Utilities (Panel/Shadow/Radius), Customer-Werte anpassen.
- [CSS-C1] App.vue scoped Layout-Overrides vs. globale Layout-Klassen (admin_frontend/admin-ui/src/App.vue:581-644) – **C (kontextabhängig)**. Scoped Override bleibt notwendig für kompakte Sidebar; in globalen Layout-Klassen nicht entfernen.
- [CSS-C2] UserCreateCard scoped Form-Layout vs. Utilities (admin_frontend/admin-ui/src/components/users/UserCreateCard.vue:64-96) – **C (kontextabhängig)**. Spezifische Gaps/Label-Styles für dieses Formular, kann später auf Utilities gemappt werden.
- [CSS-D1] Customer-Kompatibilitätsschicht in layout.css (customer_frontend/customer-ui/src/styles/layout.css:436-486) spiegelt Utilities – **D (Legacy)**. Quelle: Historische Klassen; vor Entfernung mit Nutzungsanalyse versehen und als LEGACY kommentieren.
