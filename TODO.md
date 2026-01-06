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

## CSS-Duplizierung (Klassifizierung A-D)
- [CSS-A1] Tokens Light/Dark (admin_frontend/admin-ui/src/styles/tokens.css:10-85 ↔ customer_frontend/customer-ui/src/styles/tokens.css:10-85) – **A (identisch, redundant)**. Source of Truth: docs/standards/THEME_TOKENS.md + customer_frontend/customer-ui/src/styles/tokens.css. Admin-Kopie später als LEGACY markieren.
- [CSS-B1] base.css body/app Hintergründe + Textfarbe (admin_frontend/admin-ui/src/styles/base.css:12-44 ↔ customer_frontend/customer-ui/src/styles/base.css:12-44) – **B (semantisch gleich, minimale Abweichung)**. Source of Truth: Token-Mapping auf `--surface-0`/`--text-strong` in base.css; Admin nutzt noch Legacy-Aliase (`--bg`, `--text`).
- [CSS-B2] Layout Shell/Sidebar/Nav (admin_frontend/admin-ui/src/styles/layout.css:8-127 ↔ customer_frontend/customer-ui/src/styles/layout.css:8-127) – **B (semantisch gleich, minimale Abweichung)**. Source of Truth: Admin-Layout (visuelle Referenz); Customer-Varianten sollten auf dieselbe Radius/Shadow-Skala zurückgeführt werden.
- [CSS-B3] Layout Cards/Inputs/Status/Buttons (admin_frontend/admin-ui/src/styles/layout.css:231-360 ↔ customer_frontend/customer-ui/src/styles/layout.css:231-360) – **B (semantisch gleich, minimale Abweichung)**. Source of Truth: Admin-Layout für Spacing/Radius, Customer-Input-Tokens für Farb-/Focus-States.
- [CSS-B4] Utilities page/section/chip/filter (admin_frontend/admin-ui/src/styles/utilities.css:8-122 ↔ customer_frontend/customer-ui/src/styles/utilities.css:8-122) – **B (semantisch gleich, minimale Abweichung)**. Source of Truth: Admin-Utilities (Panel/Shadow/Radius), Customer-Werte anpassen.
- [CSS-B5] Report-Filters scoped Form/Grid/Chip-Styling (customer_frontend/customer-ui/src/components/reports/ReportFilters.vue:296-372 ↔ customer_frontend/customer-ui/src/styles/utilities.css:100-160) – **B (semantisch gleich, minimale Abweichung)**. Source of Truth: Utilities; Scoped Styles als LEGACY markieren und Schrittweise auf Utilities mappen.
- [CSS-B6] Report-KPI spinner/grid (customer_frontend/customer-ui/src/components/reports/ReportKpiCards.vue:65-103 ↔ admin_frontend/admin-ui/src/styles/utilities.css:348-374) – **B (semantisch gleich, minimale Abweichung)**. Source of Truth: Utilities-Spinner/Grid; Scoped Spinner kommentieren sobald Utility-Spinner genutzt wird.
- [CSS-B7] Report-Charts spinner/grid/placeholder (customer_frontend/customer-ui/src/components/reports/ReportCharts.vue:148-193 ↔ customer_frontend/customer-ui/src/components/reports/ReportKpiCards.vue:65-103) – **B (semantisch gleich, minimale Abweichung)**. Source of Truth: Utility-Spinner + bestehende Card/Grid-Utilities; Scoped Styles als LEGACY markieren.
- [CSS-B8] Report-ExportButtons action-row (customer_frontend/customer-ui/src/components/reports/ReportExportButtons.vue:35-45 ↔ customer_frontend/customer-ui/src/styles/utilities.css:54-74) – **B (semantisch gleich)**. Source of Truth: `section-actions`/`toolbar-group`; Scoped Flex-Wrapper kommentieren und Utilities nutzen.
- [CSS-B9] AuthReauthBanner Banner/Actions (customer_frontend/customer-ui/src/components/auth/AuthReauthBanner.vue:32-84 ↔ customer_frontend/customer-ui/src/styles/utilities.css:8-52) – **B (semantisch gleich)**. Source of Truth: Section/Stack + Actions Utility; Scoped Radius/Padding als LEGACY markieren.
- [CSS-B10] UiEmptyState Panel/Stack (customer_frontend/customer-ui/src/components/ui/UiEmptyState.vue:18-44 ↔ customer_frontend/customer-ui/src/styles/utilities.css:8-52) – **B (semantisch gleich)**. Source of Truth: Section/Stack; Scoped Variant behalten wegen dashed Border, aber als LEGACY markieren.
- [CSS-B11] BaseField Hint/Error Farben (customer_frontend/customer-ui/src/components/common/BaseField.vue:24-33 ↔ customer_frontend/customer-ui/src/styles/utilities.css:114-130) – **B (semantisch gleich)**. Source of Truth: Tokens `--text-muted`/`--danger`; Legacy `--color-*` Mapping nur als Übergang.
- [CSS-B12] Badge/Counter Varianten (customer_frontend/customer-ui/src/components/layout/Topbar.vue:65-97 ↔ customer_frontend/customer-ui/src/components/layout/Sidebar.vue:67-86 ↔ customer_frontend/customer-ui/src/styles/layout.css:300-356) – **B (semantisch gleich)**. Source of Truth: Eine zentrale Badge-Utility (z.B. aus layout.css); Scoped Varianten als LEGACY kennzeichnen.
- [CSS-B13] TenantDrawer Card/Row/Input (admin_frontend/admin-ui/src/components/tenants/TenantDrawer.vue:69-115 ↔ admin_frontend/admin-ui/src/styles/layout.css:231-282) – **B (semantisch gleich)**. Source of Truth: Layout Card/Input + Utilities row-actions; Scoped Drawer-Stile als LEGACY markieren.
- [CSS-B14] AdminTenants Settings-Grid (admin_frontend/admin-ui/src/views/AdminTenantsView.vue:663-686 ↔ admin_frontend/admin-ui/src/styles/utilities.css:180-230) – **B (semantisch gleich)**. Source of Truth: form-grid/field Utilities; Scoped Grid/Gap an Utilities angleichen und als LEGACY kennzeichnen.
- [CSS-B15] AdminSettings Stack/Collapsible/Alert (admin_frontend/admin-ui/src/views/AdminSettingsView.vue:520-602 ↔ admin_frontend/admin-ui/src/styles/utilities.css:8-120) – **B (semantisch gleich)**. Source of Truth: section/stack/panel/alert Utilities; Scoped Varianten kommentieren und auf Utilities mappen.
- [CSS-B16] Modal Footer Delete-Varianten (admin_frontend/admin-ui/src/views/GlobaleArtikelView.vue:495-505 ↔ GlobaleKategorienView.vue:352-367 ↔ GlobaleEinheitenView.vue:338-347 ↔ GlobaleBranchenView.vue:892-901 ↔ admin_frontend/admin-ui/src/styles/utilities.css:501-505) – **B (semantisch gleich)**. Source of Truth: `modal__footer` in utilities; scoped Delete-Ausrichtung als LEGACY kennzeichnen und ggf. Utility-Modifier ergänzen.
- [CSS-B17] Branchen-Pane/List/Grid (admin_frontend/admin-ui/src/views/GlobaleBranchenView.vue:903-1019 ↔ admin_frontend/admin-ui/src/styles/utilities.css:140-220) – **B (semantisch gleich)**. Source of Truth: panel/list-panel/table-card Utilities; Scoped Pane/List/Grid als LEGACY markieren und auf Utilities-Gaps/Widths vereinheitlichen.
- [CSS-B18] TenantStatus Auth-Layout (customer_frontend/customer-ui/src/views/TenantStatusView.vue:80-105 ↔ customer_frontend/customer-ui/src/styles/utilities.css:241-258) – **B (semantisch gleich)**. Source of Truth: `auth-shell`/`auth-card` + `section-actions` in utilities; scoped Auth-Container als LEGACY markieren und auf Utility-Klassen mappen (Padding/Breite angleichen).
- [CSS-B19] Lagerbewegungen Badge/Callout (customer_frontend/customer-ui/src/views/LagerbewegungenView.vue:275-310 ↔ customer_frontend/customer-ui/src/styles/layout.css:539-556) – **B (semantisch gleich)**. Source of Truth: Badge/Alert in layout.css; scoped Badge-Counter/Callout als LEGACY kennzeichnen, Token-Angleichung an Badge/Alert-Utilities.
- [CSS-B20] Artikelverwaltung Page/Toolbar/Table/Form/Grid (customer_frontend/customer-ui/src/views/ArtikelverwaltungView.vue:1050-1268 ↔ customer_frontend/customer-ui/src/styles/layout.css:539-556 ↔ customer_frontend/customer-ui/src/styles/utilities.css:8-160) – **B (semantisch gleich)**. Source of Truth: page-head/toolbar/table-card/form-grid Utilities; scoped Block nutzt Legacy `--color-*` Tokens → als LEGACY markieren und auf Tokens/Utilities umstellen.
- [CSS-B21] BerichteAnalysen Spinner/Section-Stack (customer_frontend/customer-ui/src/views/BerichteAnalysenView.vue:548-586 ↔ admin_frontend/admin-ui/src/styles/utilities.css:427-438 ↔ customer_frontend/customer-ui/src/styles/utilities.css:1-60) – **B (semantisch gleich)**. Source of Truth: Utility-Spinner + section/stack; scoped Spinner/Stack als LEGACY markieren und Größen auf Utility-Spinner zurückführen.
- [CSS-B22] FehlgeschlageneBuchungen Issues/Card/Badge (customer_frontend/customer-ui/src/views/FehlgeschlageneBuchungenView.vue:415-548 ↔ customer_frontend/customer-ui/src/styles/layout.css:539-556 ↔ customer_frontend/customer-ui/src/styles/utilities.css:8-60) – **B (semantisch gleich)**. Source of Truth: section/stack/badge Utilities; scoped Karten/Badges als LEGACY markieren, Spacing/Farbwerte an Utilities angleichen.
- [CSS-B23] Toast Host/Card/Pill (admin_frontend/admin-ui/src/styles/layout.css:481-534 ↔ customer_frontend/customer-ui/src/styles/layout.css:442-495) – **B (semantisch gleich)**. Source of Truth: Admin-Toast (visuelle Referenz laut Vorgabe); Customer-Toast-Farben/Shadow als LEGACY angleichen, zentraler Toast-Utility denkbar.
- [CSS-B24] Artikelverwaltung Modal/Backdrop (customer_frontend/customer-ui/src/views/ArtikelverwaltungView.vue:1197-1243 ↔ admin_frontend/admin-ui/src/styles/utilities.css:448-506) – **B (semantisch gleich)**. Source of Truth: Utility-Modal/Backdrop; scoped Modal nutzt breitere Breite + Legacy `--color-*` Tokens → als LEGACY markieren und auf Utility-Modal/Tokens mappen.
- [CSS-B25] Auth Shell/Card Utilities (admin_frontend/admin-ui/src/styles/utilities.css:402-413 ↔ customer_frontend/customer-ui/src/styles/utilities.css:241-258) – **B (semantisch gleich)**. Source of Truth: Tokens-basierte Variante aus customer utilities (nutzt `--surface-0`/`--surface-1`); Admin-Variante verwendet Legacy `--bg` und breiteres Card-Max-Width → als LEGACY markieren und Token-Angleichung planen.
- [CSS-B26] Link/Mono Utility (admin_frontend/admin-ui/src/styles/layout.css:466-476 ↔ customer_frontend/customer-ui/src/styles/layout.css:430-437) – **B (semantisch gleich)**. Source of Truth: Tokens-basierte Link/Mono aus customer layout; Admin-Variante nutzt Legacy `--bg`/`--text` → als LEGACY markieren und Token-Mapping vereinheitlichen.
- [CSS-C1] App.vue scoped Layout-Overrides vs. globale Layout-Klassen (admin_frontend/admin-ui/src/App.vue:581-644) – **C (kontextabhängig)**. Scoped Override bleibt notwendig für kompakte Sidebar; in globalen Layout-Klassen nicht entfernen.
- [CSS-C2] UserCreateCard scoped Form-Layout vs. Utilities (admin_frontend/admin-ui/src/components/users/UserCreateCard.vue:64-96) – **C (kontextabhängig)**. Spezifische Gaps/Label-Styles für dieses Formular, kann später auf Utilities gemappt werden.
- [CSS-D1] Customer-Kompatibilitätsschicht in layout.css (customer_frontend/customer-ui/src/styles/layout.css:436-486) spiegelt Utilities – **D (Legacy)**. Quelle: Historische Klassen; vor Entfernung mit Nutzungsanalyse versehen und als LEGACY kommentieren.
