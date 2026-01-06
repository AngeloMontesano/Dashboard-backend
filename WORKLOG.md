# WORKLOG

- Datum/Uhrzeit: 2026-01-08T10:30:00Z
- Task-ID: FE-AUDIT-01
- Was analysiert/geändert: Standards unter `docs/standards` vollständig gelesen; Admin- und Customer-Frontend hinsichtlich Architektur, Routing, API-Layer, UI/UX und Styles gescannt; neue Audit- und Backlog-Dokumente angelegt; TODO neu priorisiert.
- Ergebnis: `docs/roadmap/FRONTEND_AUDIT.md` mit Standard-Zusammenfassung, Befunden, UX-Top-10 und Quick Wins pro Frontend; `docs/roadmap/FRONTEND_IMPROVEMENTS_BACKLOG.md` mit priorisierten Maßnahmen; `TODO.md` nach MUSS/SOLL/KANN aktualisiert.
- Nächste Schritte: Maßnahmen mit Teams abstimmen, Prioritäten P0/P1 adressieren (Auth-Persistenz, Logs-Endpoint, Mobile-Breakpoints, PDF-Export), optional Router-Einführung im Admin evaluieren.

- Datum/Uhrzeit: 2026-01-08T11:00:00Z
- Task-ID: FE-AUDIT-02
- Was analysiert/geändert: Feedback zu übermäßigen Admin-Toast-Meldungen und Login-Voreinstellung umgesetzt; Info-Toasts auf Fehlerfälle begrenzt und Admin-Login standardmäßig auf Benutzer/Passwort umgestellt.
- Ergebnis: Health/Navigation/Theme-Aktionen erzeugen keine Info-Toasts mehr; nur Fehlermeldungen bleiben sichtbar. Login startet im Benutzer/Passwort-Modus, reduziert Doppel-Toast-Flut.
- Nächste Schritte: Weitere Toast-Reduktion in Unterviews prüfen (z. B. Save-Erfolge gezielt), Admin-Router/Navigations-Verbesserung planen.

- Datum/Uhrzeit: 2026-01-08T12:00:00Z
- Task-ID: FE-AUDIT-03
- Was analysiert/geändert: MUSS-Empfehlungen umgesetzt: Admin-Auth wird persistiert, Logs-Tab mit Dummy-Content entfernt; Customer-Shell erhält Mobile-Breakpoint; Reporting-PDF nutzt API-Export; Bestellungen-Aktionen erhalten Row-Busy-States.
- Ergebnis: Admin-Reload behält Kontext (sessionStorage), Operations zeigt nur verfügbare Tabs; Customer-Layout stapelt unter 1100px, Reporting-PDF lädt als Datei statt Popup, Order-Buttons sind gegen Doppelaktionen geschützt.
- Nächste Schritte: Server-Paging/Validierungen (Tenants/Memberships), Queue-Confirm/A11y-Labels und Theme-Toggle in Topbar angehen.

- Datum/Uhrzeit: 2026-01-08T13:00:00Z
- Task-ID: FE-AUDIT-04
- Was analysiert/geändert: Host-Feld im Admin wrappt nun, AllowedHosts für neue Subdomains geöffnet; Admin-Settings Adresse in Straße/Hausnummer aufgeteilt; Customer Settings ebenfalls gesplittet. Reporting-PDF nutzt API-Endpunkt, Customer-API reagiert auf 401 mit Auto-Re-Login; Movement-Queue stoppt endlose Retries bei Client-Fehlern. Backend-Migrationslücke (inventory_orders) im TODO vermerkt.
- Ergebnis: Tenants-Host überläuft nicht, neue Hosts blocken nicht mehr im Vite-Server; Adresse kann strukturiert eingegeben werden; Lagerbewegungen zeigen 401/400 als Fehler ohne endlose Wiederholung; fehlende Backend-Tabellen als Must-Do dokumentiert.
- Nächste Schritte: Backend-Migration `inventory_orders` und Aggregationsfix einplanen; weitere Queue/Toast-Feinschliffe und Admin-Router-Paging umsetzen.

- Datum/Uhrzeit: 2026-01-08T14:30:00Z
- Task-ID: FE-AUDIT-05
- Was analysiert/geändert: Neue Alembic-Revision `0009_create_inventory_orders` angelegt (Orders/Order-Items-Tabellen), Reporting-Aggregation auf explizite GROUP-BY-Spalten umgestellt, TODO auf auszurollende Migration aktualisiert.
- Ergebnis: Fehlende Tabelle `inventory_orders` wird durch Migration erstellt; Reporting-Query sollte kein GROUP-BY-Fehler mehr werfen. Bereit für Deployment/Ausführung.
- Nächste Schritte: Migration auf allen Umgebungen ausführen (`alembic upgrade head`), danach Dashboard/Bestellungen/Reporting erneut testen.

## Schritt 1 – Analyse
- **Was wurde geprüft**
  - Vorgaben in `docs/` vollständig gelesen (Standards, Roadmap, OpenAPI-Kopie).
  - Vorkommen von `axios.create` gesucht:  
    - `admin_frontend/admin-ui/src/api/client.ts` (Axios-Instanz mit `getBaseURL()`, Timeout 15s).  
    - `customer_frontend/customer-ui/src/api/client.ts` (Axios-Instanz mit `getBaseURL()`, Timeout 20s, Tenant-Header-Defaults).  
    - `packages/api-client/src/index.ts` (Shared `createApiClient` mit Header-Merge und `getBaseURL()`).
  - BaseURL-/Host-Logiken identifiziert:  
    - `packages/api-client/src/index.ts` löst BaseURL über Env-Felder (`VITE_API_*`, `VITE_BASE_DOMAIN`, `VITE_API_BASE_URL`/`BASE`) und optional Runtime-Host ab; wendet `apiPrefix` an. Tenant-Header aus Host/Slug (`X-Forwarded-Host`, `X-Tenant-Slug`).  
    - `admin_frontend/admin-ui/src/api/base.ts` ruft `sharedGetBaseURL()` durch und exportiert `getBaseDomain()` (aktuell `runtimeHostname` nicht definiert).  
    - `customer_frontend/customer-ui/src/api/base.ts` re-exportiert `createApiClient`, `getBaseURL`, `getTenantHeaders`, `getTenantSlug` aus dem Shared-Paket.  
    - `admin_frontend/admin-ui` Views (`AdminDiagnosticsView`, `AdminOperationsView`, `AdminLoginView`, `App.vue`) nutzen `getBaseURL()` für Anzeige/Fehlermeldungen; Customer `auth.ts` nutzt `getBaseURL()` für Fehlermeldungen.
- **Was wurde geändert**
  - Datei `WORKLOG.md` angelegt und Analyseergebnisse dokumentiert.
- **Was ist offen**
  - Schritt 2: OpenAPI-Typen als Dev-Dependency generieren und unter `src/api/gen/openapi.ts` ablegen; lokale Spec in `docs/openapi/openapi.json` sicherstellen.  
  - Schritt 3: Axios-Clients zentralisieren (nur `src/api/client.ts` je Frontend), Basis-URL auf `/api` fixieren, übrige `axios.create` entfernen.  
  - Schritt 4: OpenAPI-Typen minimal in zentralen Wrappern nutzen.  
  - Schritt 5: Standards in `docs/standards/` ergänzen sowie `docs/roadmap/POST_MIGRATION_TASKS.md` nach Abschluss aktualisieren.

## Schritt 2 – OpenAPI-Typen
- **Was wurde geprüft**
  - OpenAPI-Skripte pro Frontend (`npm run gen:types:local`) ausgeführt gegen `docs/openapi/openapi.json`.
- **Was wurde geändert**
  - Generierte Typen für Admin (`admin_frontend/admin-ui/src/api/gen/openapi.ts`) und Customer (`customer_frontend/customer-ui/src/api/gen/openapi.ts`) aktualisiert; lokale Spec blieb unverändert.
- **Was ist offen**
  - Schritt 3: Axios-Clients zentralisieren (nur `src/api/client.ts` je Frontend), Basis-URL auf `/api` fixieren, übrige `axios.create` entfernen.  
  - Schritt 4: OpenAPI-Typen minimal in zentralen Wrappern nutzen.  
  - Schritt 5: Standards in `docs/standards/` ergänzen sowie `docs/roadmap/POST_MIGRATION_TASKS.md` nach Abschluss aktualisieren.

## Schritt 3 – Axios-Zentralisierung
- **Was wurde geprüft**
  - Sicher gestellt, dass nur noch `src/api/client.ts` je Frontend `axios.create` nutzt.
  - BaseURL-Handling auf `/api` reduziert; Host-Auflösung aus Shared-Helper entfernt.
- **Was wurde geändert**
  - Gemeinsame Helper in `packages/api-client/src/index.ts` vereinfacht (`getBaseURL()` fix auf `/api`, nur noch Header-/Slug-Hilfen ohne Axios-Instanz).
  - Admin-Client (`admin_frontend/admin-ui/src/api/client.ts`) auf zentrale Axios-Instanz mit `/api`-Basis, JSON-Headern und `adminHeaders`-Helper umgestellt; `apiClient`/`createApiClient` entfernt.
  - Admin-Basis-Helper (`admin_frontend/admin-ui/src/api/base.ts`) auf Shared-`getBaseURL` mit Runtime-Hostname-Ausgabe umgestellt; App-Kommentar an Proxy-Pfad angepasst.
  - Customer-Basis (`customer_frontend/customer-ui/src/api/base.ts`) re-exportiert nur noch Shared-Helper; Customer-Client behält zentrale Instanz mit `/api`-Basis und Tenant-Header-Defaults.
  - Customer-Wrappers (`auth.ts`, `inventory.ts`, `reporting.ts`) nutzen ausschließlich die zentrale Axios-Instanz und Header-Helper statt neuer Clients.
- **Was ist offen**
  - Schritt 4: OpenAPI-Typen minimal in zentralen Wrappern nutzen (Restabgleich und offene Kanten dokumentieren).
  - Schritt 5: Standards in `docs/standards/` ergänzen sowie `docs/roadmap/POST_MIGRATION_TASKS.md` nach Abschluss aktualisieren.

## Schritt 4 – Typ-Nutzung
- **Was wurde geprüft**
  - Offene Stellen für OpenAPI-Typen in den zentralen Wrappern identifiziert (Customer Auth/Inventory).
- **Was wurde geändert**
  - Customer-Auth nutzt das generierte Token-Response-Schema.
  - Customer-Inventory setzt Response- und Payload-Typen (Items, Categories, Movements, SKU-Check) auf die generierten OpenAPI-Schemata.
  - Reporting-Wrapper auf zentrale Axios-Instanz mit konsistenten Headern/Timeouts umgestellt; Aggregations-Fallback dokumentiert durch bestehende Fehlertexte.
- **Was ist offen**
  - Schritt 5: Standards in `docs/standards/` ergänzen sowie `docs/roadmap/POST_MIGRATION_TASKS.md` nach Abschluss aktualisieren.

## Schritt 5 – Dokumentation & QA
- **Was wurde geprüft**
  - Standards-Dokumente (`API_CLIENTS`, `FRONTEND_RULES`, `OPENAPI_TYPES`) auf neue Vorgaben (Base `/api`, fehlende Reporting-Schemaeinträge) abgeglichen.
  - Post-Migration-Tasks um neu entdeckte Lücken (Reporting-Endpunkte, VITE_API-Variablen) ergänzt.
  - Builds ausgeführt: `npm run build` in `admin_frontend/admin-ui` und `customer_frontend/customer-ui`.
- **Was wurde geändert**
  - Docs angepasst: Base-URL-Regel festgehalten, Shared-Helper ohne Axios instanziierung beschrieben, fehlende OpenAPI-Reporting-Endpunkte als Known Issue erfasst, Roadmap um Reporting/Schemabereinigung ergänzt.
  - Customer-Import-Flow typisiert (ImportResult), MovementPayload exportiert, Import-Mapping an API übergeben; PrimeVue-Initialisierung bereinigt (entfernt doppeltes Theme-Setup).
- **Was ist offen**
  - Nachziehen der dokumentierten Post-Migration-Tasks (OpenAPI-Gaps, Env-Bereinigung) und Monitoring des Bundle-Size-Warnings aus dem Customer-Build (keine Blockade).

## Nachtrag – Alias-Fix für zentrale Helfer
- **Was wurde geprüft**
  - Build-Fehler durch nicht auflösbares `@shared/api-client` in beiden Frontends.
- **Was wurde geändert**
  - `getBaseURL`/Tenant-Header-Helper pro Frontend lokal definiert (`src/api/base.ts`), Alias-Verweise in `tsconfig.json` und `vite.config.ts` entfernt.
- **Was wurde geprüft (nach Fix)**
  - `npm run build` in `admin_frontend/admin-ui` und `customer_frontend/customer-ui` erfolgreich (Customer mit bestehendem Chunk-Size-Warning).
- **Was ist offen**
  - Keine offenen Punkte aus diesem Fix; weitere To-dos siehe Post-Migration-Liste.

## Schritt 6 – Offene Tasks (Planung)
- **Was wurde geprüft**
  - Ausstehende Punkte aus `docs/roadmap/POST_MIGRATION_TASKS.md` (OpenAPI-Gaps, Reporting-Endpunkte, Env-Bereinigung).
- **Was ist geplant**
  - OpenAPI-Schema nachziehen: Admin-Login-Response, Items-Import/Export, Movements-Response, fehlender Set-Password-Endpunkt, Reporting-Endpunkte ergänzen und dann Typen regenerieren.
  - VITE-/Docker-Variablen für die Frontends bereinigen, damit nur noch der Proxy-Pfad `/api` genutzt wird.
  - Builds erneut laufen lassen.

## Schritt 7 – Umsetzung OpenAPI & Env-Bereinigung
- **Was wurde geprüft**
  - OpenAPI-Definitionen gegen Wrapper-Annahmen (Admin-Login, Tenant-Set-Password, Items-Import/Export, Movements, Reporting).
  - Docker-Compose-Variablen für beide Frontends.
- **Was wurde geändert**
  - `docs/openapi/openapi.json` ergänzt/angepasst: Admin-Login-Response, Items-Import/Export-Responses, Movement-Response-Schema, Set-Password-Endpunkt, Reporting-Endpunkte mit passenden Schemata.
  - Post-Migration-Roadmap auf Backend-Abgleich und Remote-OpenAPI fokussiert; Known Issues in `OPENAPI_TYPES.md` aktualisiert.
  - Frontend-Compose-Dateien (`docker-compose.yml`, `admin_frontend/docker-compose.yml`, `customer_frontend/docker-compose.yml`) von `VITE_API_*`-Hosts befreit (Frontends nutzen nur `/api`).
  - OpenAPI-Typen neu generiert (`npm run gen:types:local` in Admin- und Customer-Frontend).
- **Was ist offen**
  - Backend-Abgleich zu den neuen OpenAPI-Spezifikationen (siehe Roadmap) sowie Klärung des Remote-OpenAPI-Zugriffs.

## Schritt 8 – Verifikation
- **Was wurde geprüft**
  - Frontend-Builds nach Schema-/Env-Anpassungen.
- **Was wurde geändert**
  - Builds erfolgreich ausgeführt: `npm run build` in `admin_frontend/admin-ui` und `customer_frontend/customer-ui` (Customer mit bekannter Chunk-Size-Warnung).
- **Was ist offen**
  - Keine zusätzlichen QA-Punkte; bestehende Chunk-Warnung nur beobachten.

## Schritt 9 – Offene Punkte aktualisiert
- **Was wurde geprüft**
  - Übrig gebliebene Roadmap-Punkte nach Proxy-Zugriff auf `/api/openapi.json`.
- **Was wurde geändert**
  - Roadmap um den erledigten Remote-Zugriff bereinigt; Known Issues verweisen auf Proxy-Zugriff als Quelle und auf Backend-Bestätigung.
- **Was ist offen**
  - Backend-Abgleich der OpenAPI-Definitionen bleibt ausstehend.

## Schritt 10 – Remote-OpenAPI-Verifikation
- **Was wurde geprüft**
  - Erneuter Zugriff auf das entfernte Schema: `curl https://api.test.myitnetwork.de/api/openapi.json` und `curl http://api.test.myitnetwork.de/api/openapi.json` (beide 403).
- **Was wurde geändert**
  - Roadmap und Standards aktualisiert: Remote-Schema bleibt gesperrt (403), Nutzung der lokalen Kopie bleibt notwendig, Backend-Abgleich weiterhin offen.
- **Was ist offen**
  - Backend/Schema-Abgleich der erweiterten OpenAPI-Definitionen.
  - Freischaltung oder Zugriffspfad für `/api/openapi.json` (aktuell 403) klären, damit `gen:types` ohne lokale Kopie lauffähig ist.

## Schritt 11 – Lokale Typ-Generierung als Standard
- **Was wurde geprüft**
  - Skripte zur Typ-Generierung in beiden Frontends.
- **Was wurde geändert**
  - `gen:types` in Admin- und Customer-Frontend nutzen jetzt standardmäßig `docs/openapi/openapi.json`; optionales `gen:types:remote` verweist auf `/api/openapi.json`.
  - Roadmap und Standards angepasst: Lokale Spec ist verbindlich, Remote-Zugriff optional.
- **Was ist offen**
  - Backend/Schema-Abgleich der erweiterten OpenAPI-Definitionen bleibt offen; Remote-Zugriff ist kein Blocker mehr.

## MIG-CUST-UI-PARITY – Phase 2 Start
- Datum/Uhrzeit: 2026-01-08T15:00:00Z
- Task-ID: MIG-CUST-UI-PLAN
- Plan vor Umsetzung: Phase-2-Vorbereitung – Dokumentation anlegen/aktualisieren (`docs/roadmap/CUSTOMER_UI_PARITY_WITH_ADMIN.md`, `TODO.md` Scope neu priorisieren, `WORKLOG.md` fortschreiben) und anschließend Admin-Styles in das Customer-Frontend übernehmen (Tokens/Base/Layout/Utilities), bevor die Layout-Shell vereinheitlicht wird.
- Ergebnis: Roadmap erstellt (`docs/roadmap/CUSTOMER_UI_PARITY_WITH_ADMIN.md`), TODO priorisiert auf PrimeVue-Removal/Parity-Fokus, WORKLOG-Eintrag für Phase 2 angelegt.
- Nächste Schritte: Nach Dokumentation Admin-Styles kopieren (Task MIG-CUST-UI-STYLE), dann Layout-Shell auf Admin-Struktur heben (Task MIG-CUST-UI-SHELL).

- Datum/Uhrzeit: 2026-01-08T15:10:00Z
- Task-ID: MIG-CUST-UI-STYLE
- Plan vor Umsetzung: Admin-Styles (tokens/base/layout/utilities) ins Customer-Frontend übernehmen, Token-Aliaising für bestehende Customer-Variablen erhalten, PrimeVue-spezifische Selektoren aus Layout entfernen und globale Importe (main.ts) auf neue Styles ergänzen. Keine Funktionalitätsänderung, nur Styling-Grundlagen.
- Ergebnis: Admin-Token/Style-Dateien übernommen (`src/styles/tokens.css`, `base.css`, `layout.css`, `utilities.css`), Legacy-Aliasse für vorhandene Customer-Klassen ergänzt, PrimeVue-spezifische Selektoren entfernt. `main.ts` lädt jetzt `base.css`. Das Layout nutzt nun Admin-Farb-/Spacing-Tokens und Toast-/Button-Kompatibilität.
- Geänderte Dateien: `customer_frontend/customer-ui/src/styles/tokens.css`, `customer_frontend/customer-ui/src/styles/base.css` (neu), `customer_frontend/customer-ui/src/styles/layout.css`, `customer_frontend/customer-ui/src/styles/utilities.css`, `customer_frontend/customer-ui/src/main.ts`.
- Nächste Schritte: Nach Style-Übernahme Layout-Shell/Komponenten auf Admin-Struktur anpassen (Task MIG-CUST-UI-SHELL).

- Datum/Uhrzeit: 2026-01-08T15:25:00Z
- Task-ID: MIG-CUST-UI-SHELL
- Plan vor Umsetzung: App-Shell (App.vue, Sidebar, Topbar, ToastHost) auf Admin-Struktur bringen: Klassen/Markup an Admin-Layout angleichen, Toast-Komponente auf Admin-Toast-Styles umstellen, Root-Class auf `.app` für neuen Base-Style setzen. Keine PrimeVue-Abhängigkeiten hinzufügen.
- Ergebnis: App-Shell nutzt nun `.app` + `.shell` Layout (Admin-Grid), Sidebar/Topbar-Markup auf Admin-Navigation/Topbar-Klassen umgestellt, ToastHost rendert im Admin-Stil (`toastHost`/`toastCard`). Login nutzt `auth-shell` Background-Gradient, Toast global statt doppelt. Theme-Class bleibt `theme-dark` only.
- Geänderte Dateien: `customer_frontend/customer-ui/src/App.vue`, `customer_frontend/customer-ui/src/components/layout/Sidebar.vue`, `customer_frontend/customer-ui/src/components/layout/Topbar.vue`, `customer_frontend/customer-ui/src/components/common/ToastHost.vue`.
- Nächste Schritte: Nach Shell-Angleichung PrimeVue entfernen und Reporting-Komponenten ersetzen (Task MIG-CUST-UI-PRIME).

- Datum/Uhrzeit: 2026-01-08T15:40:00Z
- Task-ID: MIG-CUST-UI-PRIME
- Plan vor Umsetzung: PrimeVue aus dem Customer-Frontend entfernen (package.json/lock, main.ts Plugins/Imports, CSS), alle PrimeVue-Komponenten in Reports/Dashboard durch native oder bestehende UI ersetzen (Dropdown/MultiSelect/Calendar/DataTable/Card/Button/Toast/Spinner/Tag/Chart). Falls Ersatz minimal, einfache Inputs/Selects/Tabellen nutzen und TODOs markieren. Danach Build prüfen.
- Ergebnis: PrimeVue-Dependencies entfernt (package.json/lock, main.ts), Reports-UI auf native/Admin-Stil umgestellt: Filter mit nativen Date-/Select-Inputs + Chips, Export-Buttons mit Admin-Buttons, KPI/Charts mit eigenen Spinnern und Chart.js Canvas-Rendering, Tabelle ohne DataTable/Tag. Toasts nutzen internes Toast-System. PrimeVue-Imports/-CSS vollständig eliminiert. Build verifiziert (`npm run build` im Customer).
- Geänderte Dateien: `customer_frontend/customer-ui/package.json`, `customer_frontend/customer-ui/package-lock.json`, `customer_frontend/customer-ui/src/main.ts`, `customer_frontend/customer-ui/src/components/reports/ReportFilters.vue`, `customer_frontend/customer-ui/src/components/reports/ReportExportButtons.vue`, `customer_frontend/customer-ui/src/components/reports/ReportKpiCards.vue`, `customer_frontend/customer-ui/src/components/reports/ReportCharts.vue`, `customer_frontend/customer-ui/src/views/BerichteAnalysenView.vue`.
- Nächste Schritte: Nach Removal gezielte View-Politur pro Screen (Phase 4) und abschließender Build/PrimeVue-Grep.

- Datum/Uhrzeit: 2026-01-08T16:10:00Z
- Task-ID: MIG-CUST-UI-VIEWS
- Plan vor Umsetzung: Phase 4 starten – zentrale Views auf Admin-Look heben (Cards/Sections/Buttons/Tables) ohne Logikänderungen. Fokus: Dashboard, Artikelverwaltung, Lagerbewegungen, Inventur, Bestellungen, Einstellungen. Struktur auf `UiPage`/`section`-Pattern, Buttons auf `btnPrimary/btnGhost`, Tabellen auf `.tableWrap/.table`, Banner/Filterleisten auf Admin-Stil. Danach Build und PrimeVue-Grep zur Sicherung.
- Ergebnis: Buttons/Tabellen/Banner kompatibel zum Admin-Stil harmonisiert (btnPrimary/btnGhost, tableWrap/table, Banner/Alert/Badges/SR-only Styles in `layout.css`/`utilities.css`). Views angepasst: Dashboard Action-Button, Lagerbewegungen (Buttons/TableWrap), Inventur (Buttons/Banner/TableWrap), Artikelverwaltung (Header/Detail-/Create-/Import-Buttons), Einstellungen (Toolbar/Testmail Buttons). Compatibility-Layer ergänzt für page-head, alerts, badges, pagination, toolbar-fields, sr-only. TODO aktualisiert (Rest-Views Bestellungen/Kategorien-Feinschliff). Build folgt.
- Geänderte Dateien: `customer_frontend/customer-ui/src/styles/layout.css`, `customer_frontend/customer-ui/src/styles/utilities.css`, `customer_frontend/customer-ui/src/views/DashboardView.vue`, `customer_frontend/customer-ui/src/views/LagerbewegungenView.vue`, `customer_frontend/customer-ui/src/views/InventurView.vue`, `customer_frontend/customer-ui/src/views/ArtikelverwaltungView.vue`, `customer_frontend/customer-ui/src/views/EinstellungenView.vue`, `TODO.md`.
- Nächste Schritte: Restliche Views (Bestellungen/Kategorien) und Detail-Politur prüfen, dann finalen Build/PrimeVue-Grep und visuelle Kontrolle Dark-Mode.

- Datum/Uhrzeit: 2026-01-08T16:40:00Z
- Task-ID: MIG-CUST-UI-VIEWS-2
- Plan vor Umsetzung: Phase 4 fortsetzen – verbleibende Views (Kategorien, Bestellungen, Berichte-Feinschliff) auf Admin-Stil finalisieren: Buttons auf btnPrimary/btnGhost, Tabellen in tableWrap/table, Banner/Empty States vereinheitlichen, Filterleisten an Utilities anlehnen. Anschließend Build + PrimeVue-Grep.
- Ergebnis: Kategorien/Bestellungen/Login auf Admin-Button-Pattern umgestellt, Tabellen auf `tableWrap/table`, Aktionen in Bestellungen/Kategorien auf btnPrimary/btnGhost, Create-Bestellung-Tabelle harmonisiert. Login-Button an Admin-Stil angepasst. Tabelle/Wrap in Artikelverwaltung korrigiert. ROADMAP-Checkliste aktualisiert (Build/PrimeVue entfernt, Styling-Fortschritt). TODO um Rest-Politur fokussiert.
- Geänderte Dateien: `customer_frontend/customer-ui/src/views/KategorienView.vue`, `customer_frontend/customer-ui/src/views/BestellungenView.vue`, `customer_frontend/customer-ui/src/views/LoginView.vue`, `customer_frontend/customer-ui/src/views/ArtikelverwaltungView.vue`, `customer_frontend/customer-ui/src/styles/layout.css`, `customer_frontend/customer-ui/src/styles/utilities.css`, `docs/roadmap/CUSTOMER_UI_PARITY_WITH_ADMIN.md`, `TODO.md`, `WORKLOG.md`.
- Nächste Schritte: Optional weitere View-Politur/QA Dark-Mode; finaler Build/PrimeVue-Grep erfolgt.

## Schritt 12 – UI-Harmonisierung Task 1 (Ist-Aufnahme)
- **Datum/Uhrzeit**: 2026-01-05T15:43:05+00:00
- **Ziel**: Bestandsaufnahme für Design-Harmonisierung (Global Styles, PrimeVue, Tokens, Layout-Bausteine) in Admin- und Customer-Frontend.
- **Was wurde geprüft**
  - Admin (`admin_frontend/admin-ui`): globale Styles liegen in `src/styles/{tokens,base,layout}.css` und werden in `src/main.ts` geladen; kein PrimeVue-Einsatz; Theme-Klassen (`theme-dark`, `theme-ocean`, `theme-classic`) werden in `App.vue` gesetzt und in `sessionStorage` persistiert; Toast-Markup zentral in `components/common/ToastHost.vue`; Layout/Buttons/Cards/Table-Styles in `layout.css`.
  - Customer (`customer_frontend/customer-ui`): globale Styles in `src/styles/{tokens,layout}.css`, Import in `src/main.ts`; PrimeVue mit Lara-Preset und ToastService in `main.ts`, Prime-Komponenten v. a. in `views/BerichteAnalysenView.vue` und `components/reports/*`; Theme-State via `useTheme` (SessionStorage) nur als Klassenwechsel am App-Root; Sidebar/Topbar als eigene Layout-Komponenten; Toast-Markup in `components/common/ToastHost.vue`.
  - Redundanzen: getrennte Button-/Card-/Table-Klassen beider Apps; zwei Token-Sets ohne gemeinsame Struktur; kein System-Default für Theme in beiden Apps; Toast/Overlay-Styles pro App separat definiert; Responsive-Regeln unterschiedlich (Admin über `.shell` Breakpoint, Customer mit Grid/Sidebar ohne mobile Stacking-Strategie).
- **Was wurde geändert**
  - TODO-Liste angelegt (`TODO.md`) mit Muss/Soll/Kann für Tokens, Utilities, Theme-Toggle, Toast/Responsive-Aufgaben.
  - Neue Standards in `docs/standards/`: `DESIGN_SYSTEM.md`, `THEME_TOKENS.md`, `COMPONENT_CONVENTIONS.md`, `DARKMODE.md` zur Dokumentation der Zielarchitektur (Tokens, Utilities, UI-Bausteine, Dark-Mode-Vorgaben).
- **Ergebnis**
  - Ist-Zustand pro App dokumentiert; zentrale Leitplanken für die nächsten Tasks festgelegt, keine Code-/Layout-Änderungen vorgenommen.
- **Nächster Schritt**
  - Task 2: Design-Tokens je App vereinheitlichen und um Light/Dark erweitern (inkl. System-Default-Konzept aus den neuen Standards).

## Schritt 13 – UI-Harmonisierung Task 2 (Theme Tokens)
- **Datum/Uhrzeit**: 2026-01-05T15:53:43+00:00
- **Ziel**: Theme-Tokens für beide Frontends finalisieren und konsistent einführen (Light/Dark), ohne View-Refactors.
- **Was wurde geprüft**
  - Vorhandene Token-Namen in Admin (`--bg`, `--panel`, Tags/Status) und Customer (`--color-*`) für Kompatibilität beibehalten.
  - Dark-/Ocean-Klassen werden derzeit als Klassen statt `data-theme` gesetzt; Mapping musste kompatibel bleiben.
- **Was wurde geändert**
  - Admin: `src/styles/tokens.css` auf die gemeinsame Token-Struktur (Surfaces/Text/Status/Spacing/Radius/Focus) umgestellt, neue Standard-Tokens ergänzt und bestehende Variablen über Legacy-Mappings erhalten (Light/Dark/Ocean).
  - Customer: `src/styles/tokens.css` um dieselbe Token-Struktur erweitert, inklusive Legacy-Mappings für bestehende Klassen und PrimeVue-Layouts; Light/Dark/Ocean nutzen jetzt die abgestimmten Tokens.
- **Ergebnis**
  - Beide Frontends besitzen ein deckungsgleiches Token-Set (Light/Dark) mit kompatiblen Alt-Namen; keine View- oder Komponenten-Anpassungen nötig.
- **Nächster Schritt**
  - Task 3: Utilities/Theme-Mappings ergänzen und erste Pilot-Views auf Utilities umstellen (separater Schritt).

## Schritt 14 – UI-Harmonisierung Task 3 (Utilities + Pilot-Views)
- **Datum/Uhrzeit**: 2026-01-05T16:00:46+00:00
- **Ziel**: Basis-Utilities pro App bereitstellen und je eine Pilot-View auf die neuen Klassen umstellen.
- **Was wurde geändert**
  - Admin: `src/styles/utilities.css` angelegt (page/section/stack/toolbar/chips/cards/detail/flex Utilities) und in `main.ts` importiert; `AdminUsersView` nutzt jetzt ausschließlich die neuen Utilities ohne scoped Styles.
  - Customer: `src/styles/utilities.css` angelegt (page/section/stack/toolbar/card-grid) und in `main.ts` importiert; `DashboardView` auf die Utilities umgestellt.
  - TODO aktualisiert: Utilities vorhanden, weitere Views sukzessive umstellen.
- **Ergebnis**
  - Gemeinsame Layout-Basis pro App ist verfügbar; erste View pro App validiert die Utilities.
- **Nächster Schritt**
  - Weitere Views auf Utilities/UI-Komponenten migrieren, Theme-Steuerung (System/LocalStorage) und zentrale Toast/Overlay-Styles umsetzen.

## Schritt 15 – UI-Harmonisierung Task 4 (UI-Bausteine + weitere Piloten)
- **Datum/Uhrzeit**: 2026-01-05T16:09:10+00:00
- **Ziel**: Zentrale UI-Bausteine je App anlegen und je eine View auf die Bausteine umstellen.
- **Was wurde geändert**
  - Admin: Neue UI-Komponenten (`UiPage`, `UiSection`, `UiCard`, `UiStatCard`, `UiToolbar`, `UiEmptyState`) unter `src/components/ui`; Utilities um Ausrichtungs-/Fehlerklassen ergänzt; `AdminUsersView` nutzt jetzt die UI-Bausteine statt eigener Layout-Elemente.
  - Customer: Entsprechende UI-Komponenten unter `src/components/ui` angelegt; `DashboardView` auf `UiPage`/`UiSection`/`UiStatCard` umgestellt.
- **Ergebnis**
  - Gemeinsame UI-Baustein-Basis pro App verfügbar; zwei Pilot-Views validieren die Nutzung ohne Inline-/Scoped-Styles für Layout/Spacing.
- **Nächster Schritt**
  - Weitere Kern-Views (Customer: Lagerbewegungen, Berichte & Analysen; Admin: Tenants/Memberships/Operations) auf die UI-Bausteine migrieren; anschließend Theme-Toggle/System-Default und zentrale Toast/Overlay-Styles umsetzen.

## Schritt 16 – UI-Harmonisierung Task 5 (Theme-System + Toggles)
- **Datum/Uhrzeit**: 2026-01-05T16:15:00+00:00
- **Ziel**: Dark/Light/System-Theme mit Persistenz pro App einführen und bestehende Toggles vereinheitlichen.
- **Was wurde geändert**
  - Admin: Neues `useTheme` (System/Light/Dark, localStorage, `data-theme` auf `<html>`), Init in `main.ts`; App-Root nutzt resolved Theme; Sidebar-Select für Theme; Settings-View nutzt die neuen Theme-IDs.
  - Customer: `useTheme` auf System-Default umgestellt, Init in `main.ts`; App-Root nutzt resolved Theme; Topbar erhält Theme-Select ohne Inline-Styles; Utilities ergänzt (`inline-field`).
- **Ergebnis**
  - Beide Apps setzen Themes zentral über `data-theme` und persistieren im localStorage; Toggles in UI verfügbar.
- **Nächster Schritt**
  - Weitere Views auf UI-Bausteine/Utilities migrieren; zentrale Toast/Dialog-Styles harmonisieren; optional System-Listener für Theme-Änderung ergänzen.

## Schritt 17 – UI-Harmonisierung Task 5b (System-Listener)
- **Datum/Uhrzeit**: 2026-01-05T16:22:29+00:00
- **Ziel**: System-Theme-Änderungen automatisch berücksichtigen, wenn der Mode auf „system“ steht.
- **Was wurde geändert**
  - Admin: `useTheme` ergänzt um `matchMedia`-Listener, der bei Systemwechsel das Theme neu anwendet.
  - Customer: Gleiches Verhalten in `useTheme`, Listener wird einmalig registriert.
- **Ergebnis**
  - Bei Systemwechsel wird das aktive Theme aktualisiert, solange der Modus auf „system“ steht; Persistenz bleibt in `localStorage`.
- **Nächster Schritt**
  - Weitere Views migrieren und Toast/Dialog-Styles zentralisieren; Theme-Toggle-UI ggf. verfeinern (Dropdown/Icons) ohne Inline-Styles.

## Schritt 18 – UI-Harmonisierung (Tenants/Memberships + Modals)
- **Datum/Uhrzeit**: 2026-01-05T16:41:01+00:00
- **Ziel**: Weitere Admin-Views auf zentrale Utilities/UI-Bausteine heben und Modal-/Overlay-Styles tokenbasiert angleichen.
- **Was wurde geändert**
  - Admin-Utilities erweitert (Form-/Detail-/KV-Grids, Tabs, Modal-Backdrops/-Panels, Spacing/BADGE/Spinner) und Table/Detail-Hilfsklassen ergänzt.
  - `AdminTenantsView` auf `UiPage`/`UiSection`/`UiToolbar`/`UiStatCard` + Utilities umgestellt; scoped Styles entfernt, Filter-/Detail-/Table-Layouts nutzen jetzt tokenisierte Klassen.
  - `AdminMembershipsView` gleichermaßen auf die UI-Bausteine migriert; Listen-, Filter- und Detailbereiche ohne scoped Styles, Buttons/Badges nutzen zentrale Tokens.
  - Tenant-Create-Modal auf zentrale Modal-/Backdrop-Utilities umgestellt, inline Styles entfernt.
- **Ergebnis**
  - Zwei weitere Kern-Views im Admin folgen den harmonisierten Layout-Utilities ohne Inline-/Scoped-Styles; Modal/Overlay-Optik nutzt zentrale Token-Variablen.
- **Nächster Schritt**
  - Restliche Admin-Views (Diagnostics/Operations/Audit/Login/Kunden) und Customer-Views schrittweise auf die Utilities/Komponenten ziehen; zentrale Toast/Overlay-Styles finalisieren und responsive Regeln nachziehen.

## Schritt 19 – UI-Harmonisierung (Admin Login/Diagnostics/Operations)
- **Datum/Uhrzeit**: 2026-01-05T16:50:16+00:00
- **Ziel**: Weitere Admin-Views auf Utilities/UI-Bausteine heben und Inline-Styles entfernen.
- **Was wurde geändert**
  - Utilities ergänzt (auth-shell/-card, code-block, Text-Tones, push-right) für wiederverwendbare Auth-/Log-/Hint-Layouts.
  - `AdminLoginView` auf `UiPage` und Layout-Utilities umgestellt, Statusfarben über Tokens statt scoped Styles.
  - `AdminOperationsView` auf `UiPage`/`UiSection` migriert, Tabs/Panels/Audit/Snapshot/Logs ohne Inline-Styles; nutzt neue code-/pill-/action-Utilities.
  - `AdminDiagnosticsView` analog auf UI-Bausteine und Utilities gehoben; Health/Snapshot/Logs ohne Inline-Styles.
  - Audit-Filter-Bar und Kunden-Demo-Support/Hints auf Utility-Klassen umgestellt (keine inline `style=` mehr).
- **Ergebnis**
  - Drei weitere Admin-Ansichten sowie Audit-Filter nutzen zentrale Utilities und tokenbasierte Farben/Abstände; Inline- und scoped Styles entfernt.
- **Nächster Schritt**
  - Admin: Audit-View und Kunden-Demo weiter auf Utilities bringen; Toast/Overlay-Styling zentralisieren. Customer: übrige Views migrieren.

## Schritt 20 – UI-Harmonisierung (Audit + Customer Lagerbewegungen)
- **Datum/Uhrzeit**: 2026-01-05T16:57:20+00:00
- **Ziel**: Audit-View und erste Customer-Transaktions-View auf Utilities/UI-Bausteine heben, Inline-Styles entfernen.
- **Was wurde geändert**
  - Audit-View auf `UiPage`/`UiSection` + Utility-Layout (action-row, stack-sm, text-muted) umgestellt; Pagination-Hinweise tokenisiert, Buttons ohne inline Styles.
  - Customer-Utilities um Form-Grids, Action-Rows, Text-Farben und Spacing-Helper erweitert.
  - Customer `LagerbewegungenView` auf `UiPage`/`UiSection`/`UiToolbar` und neue Utilities refaktoriert; Status/Error-Anzeigen nutzen Token-Klassen statt inline Farbwerte.
  - Audit-Filter-Bar und Kunden-Demo (KundenView) nutzen Utility-Klassen (Form-Grid, Pill-Row, Action-Row) statt inline Styles.
- **Ergebnis**
  - Audit und Lagerbewegungen folgen nun den harmonisierten Layout-Utilities; weitere Inline-/Scoped-Styling reduziert, Token-Farben greifen für Status/Error-Anzeigen.
- **Nächster Schritt**
  - Admin: Kunden-View auf Utilities bringen und Toast/Overlays zentralisieren. Customer: weitere Views (Artikel/Kategorien/Berichte/Inventur/Bestellungen/Einstellungen/Login) migrieren und responsive Regeln prüfen.

## Schritt 21 – UI-Harmonisierung (KundenView + Kategorien)
- **Datum/Uhrzeit**: 2026-01-05T17:03:00+00:00
- **Ziel**: Admin Kunden-Workspace vollständig auf UI-Bausteine heben und Customer Kategorien-View auf Utilities ausrichten.
- **Was wurde geändert**
  - Admin `KundenView` auf `UiPage`/`UiCard` + Utility-Form/Grid/Text-Klassen umgestellt; alte Grid/Card-Markup und Inline-Hints entfernt.
  - Customer `KategorienView` auf `UiPage`/`UiSection`/`UiToolbar` und Utility-Action/Form-Grids refaktoriert; Inline-Styles entfernt, Inputs nutzen gemeinsame Klassen.
- **Ergebnis**
  - Kunden-Workspace und Kategorien-Management sind nun tokenbasiert gestylt und nutzen die zentralen Layout-Utilities ohne scoped/inline Styles.
- **Nächster Schritt**
  - Customer: verbleibende Views (Artikel/Berichte/Inventur/Bestellungen/Einstellungen/Login) migrieren. Admin: zentrale Toast/Overlay-Styles finalisieren.

## Schritt 22 – UI-Harmonisierung (Customer Login/Inventur/Bestellungen/Einstellungen)
- **Datum/Uhrzeit**: 2026-01-05T17:12:28+00:00
- **Ziel**: Weitere Customer-Views auf UiPage/UiSection und Utilities heben; Inline-Styles entfernen.
- **Was wurde geändert**
  - Utilities (customer) um Auth-Shell/Card, Text-Tones und Action/Form-Spacing ergänzt.
  - Login-View auf UiPage + Auth-Utilities umgestellt; scoped Styles entfernt, Inputs nutzen gemeinsame Klassen.
  - Inventur-, Bestellungen- und Einstellungen-Views auf UiPage/UiSection/UiToolbar plus Utility-Spacing migriert; Inline-Styles (margin) entfernt.
  - Artikelverwaltung: verbliebene Inline-Margins durch Utility-Klassen ersetzt.
- **Ergebnis**
  - Customer Auth/Dashboard-ähnliche Static Views nutzen jetzt die zentralen Layout-Bausteine; Inline-Styles reduziert, Tokens greifen für Status-/Textfarben.
- **Nächster Schritt**
  - Customer: Artikelverwaltung und Berichte vollständig auf UiPage/UiSection/Utilities heben (inkl. PrimeVue-Parts) und restliche Inline/Scoped-Styles abbauen. Admin: Overlay/Toast-Styling finalisieren.

## Schritt 23 – Legacy-Migration Phase 0–2 (Reverse Engineering & Gap-Liste)
- **Datum/Uhrzeit**: 2026-01-05T18:05:00+00:00
- **Ziel**: Legacy-Funktionen aus `/old_lm` analysieren, Scope/DoD festlegen und Soll-Ist-Gaps dokumentieren.
- **Was wurde geprüft**
  - Legacy-Module gelesen: `artikel.py`, `bestandsverwaltung.py`, `inventur.py`, `berichte.py`, `bestellungen.py`, `einstellungen.py`, `flash.py`, `dashboard.py`.
  - Aktuelles Backend/Frontend gecheckt (Inventar-Router, Reporting-Fallback in Frontend, fehlende Bestellungen/Einstellungen-APIs).
- **Was wurde geändert**
  - Neue Roadmap-Datei `docs/roadmap/MIGRATION_OLD_LM.md` mit Scope, DoD, Decisions, Funktionsmatrix und Gap-Liste angelegt.
  - Task-Liste erstellt: `docs/roadmap/TASKS_MIGRATION_OLD_LM.md` mit IDs T1–T8 (Backend/Customer/Docs).
  - TODO erweitert um Must-Haves für Legacy-Migration (Backend-Endpunkte, Frontend-Datenverdrahtung, OpenAPI-Nachzug).
- **Ergebnis**
  - Reverse Engineering abgeschlossen; Gaps klar dokumentiert; Tasks strukturiert.
- **Nächster Schritt**
  - T1: Backend GET `/inventory/movements` + OpenAPI/Schemas, dann weitere Tasks laut Roadmap.

## Schritt 24 – Legacy-Migration Phase 3 Start (T1: GET Bewegungen)
- **Datum/Uhrzeit**: 2026-01-05T18:30:00+00:00
- **Ziel**: Bewegungs-Listing für Reporting/Audit ergänzen (Filter + Limit), Basis für Berichte und Inventur.
- **Was wurde geändert**
  - Backend: Neuer GET `/inventory/movements` mit Filtern (Zeitraum, Typ, Kategorie, Items) und Limit; Response liefert Artikel-Infos.
  - Schemas: `MovementOut`/`MovementItemOut` ergänzt.
  - OpenAPI: Pfad + Schemas für Bewegungs-Listing hinzugefügt.
  - Roadmap/TODO aktualisiert: Gap „GET Bewegungen“ geschlossen, Must-Liste angepasst.
- **Ergebnis**
  - Bewegungen sind tenant-sicher abrufbar und filterbar; Grundlage für Reporting-Backend/Frontend.
- **Nächster Schritt**
  - T2/T3 vorbereiten: Inventur-Bulk/Export und Reporting-Endpunkte implementieren, OpenAPI + Typen nachziehen.

## Schritt 25 – Legacy-Migration Phase 3 (T2: Inventur Bulk + Export)
- **Datum/Uhrzeit**: 2026-01-05T19:00:00+00:00
- **Ziel**: Inventur-APIs bereitstellen (Bulk-Update & Excel-Export) als Grundlage für Customer-Frontend.
- **Was wurde geändert**
  - Backend: Neuer POST `/inventory/inventory/bulk` (Tenant-scoped, Owner/Admin) für Mengen-Updates per Item-ID; GET `/inventory/inventory/export` liefert Excel (`inventur.xlsx`) mit Legacy-Spalten (Artikel-ID, Name, Barcode, Kategorie, Soll, Min, Bestand).
  - Schemas: `InventoryUpdate`, `InventoryBulkUpdateRequest`, `InventoryBulkUpdateResult` ergänzt.
  - OpenAPI: Pfade und Schemas für Inventur-Bulk/Export hinzugefügt.
  - Roadmap/TODO: Gap „Inventur-API“ als erledigt markiert; Must-Liste angepasst.
- **Ergebnis**
  - Inventur-Daten sind per API aktualisier- und exportierbar; Excel folgt Legacy-Spalten, Tenant-Isolation gewährleistet.
- **Nächster Schritt**
  - T3: Reporting-Endpunkte (/inventory/report + Exporte) implementieren; anschließend Frontend an Inventur/Reporting anbinden.

## Schritt 26 – Legacy-Migration Phase 3 (T3: Reporting)
- **Datum/Uhrzeit**: 2026-01-05T19:30:00+00:00
- **Ziel**: Serverseitige Verbrauchs-Reports inkl. CSV/XLSX-Export bereitstellen.
- **Was wurde geändert**
  - Backend: GET `/inventory/report` und `/inventory/reports/consumption` liefern aggregierte Verbrauchsdaten (OUT-Bewegungen) nach Zeitraum, Modus (top5/all/selected), Kategorie/Items, optional aggregiert.
  - Backend: GET `/inventory/reports/export/{format}` erzeugt CSV/XLSX mit Artikeln, Monat, Verbrauch; nutzt dieselbe Aggregation.
  - Schemas: ReportDataPoint/Series/Kpis/Response ergänzt; OpenAPI bereits vorhanden, jetzt implementiert.
  - TODO/Roadmap aktualisiert: Reporting-Gap geschlossen.
- **Ergebnis**
  - Verbrauchsberichte laufen serverseitig; Exporte stehen bereit; Grundlage für Frontend-Anbindung ohne Client-Fallback.
- **Nächster Schritt**
  - Nächste Pflichtbereiche: Bestellungen (Models/Endpoints) und Einstellungen/Firmendaten inkl. Mass Import/Export umsetzen; Frontend an neue Reporting-/Inventur-APIs anbinden.

## Schritt 27 – Legacy-Migration Phase 3 (T4 Teilschritt: bestellwürdig-Liste)
- **Datum/Uhrzeit**: 2026-01-05T19:45:00+00:00
- **Ziel**: Bestellwürdige Artikel serverseitig bereitstellen.
- **Was wurde geändert**
  - Backend: GET `/inventory/orders/recommended` liefert aktive Items unter Zielbestand (tenant-scope).
  - Schemas/OpenAPI: ReorderItem/ReorderResponse ergänzt; Roadmap/TODO angepasst (Bestellungen teilweise geschlossen).
  - Empfehlung ergänzt: `recommended_qty` (max Zielbestand-Lücke vs. Mindestbestand), Sortierung nach Lücke.
- **Ergebnis**
  - Bestellwürdige Liste verfügbar; weitere Bestell-Features (offen/erledigt, Bestandserhöhung, PDF/E-Mail) noch offen.
- **Nächster Schritt**
  - Vollständige Bestell-Endpunkte und Einstellungen/Firmendaten implementieren; Customer-Frontend anbinden.

## Schritt 28 – Customer Reporting an Backend angebunden
- **Datum/Uhrzeit**: 2026-01-05T20:00:00+00:00
- **Ziel**: Frontend-Reporting nutzt den neuen Backend-Report-Endpoint und Exporte.
- **Was wurde geändert**
  - `customer_frontend` Reporting-API ruft jetzt `/inventory/report` und `/inventory/reports/export/{format}`; Client-Aggregations-Fallback entfernt.
  - OpenAPI-Typen werden für Response-Adaptierung genutzt; Export-Path aktualisiert.
- **Ergebnis**
  - Berichte & Analysen nutzen serverseitige Aggregation und Exporte; kein Bewegungs-Fallback mehr.
- **Nächster Schritt**
  - Bestell-Endpunkte (offen/erledigt) und Einstellungen/Firmendaten im Backend ergänzen; Customer-Views auf neue APIs heben.

## Schritt 29 – Legacy-Migration Phase 3 (T4: Bestellungen Grundfunktionen)
- **Datum/Uhrzeit**: 2026-01-05T20:30:00+00:00
- **Ziel**: Bestell-CRUD inkl. Erledigt-/Storno-Flow ergänzen und Bestandserhöhung abbilden.
- **Was wurde geändert**
  - Backend: Neue Modelle `InventoryOrder`/`InventoryOrderItem` (Tenant-scoped) inkl. Nummern-Constraint.
  - Endpunkte: `/inventory/orders` (GET/POST), `/inventory/orders/{id}` (GET), `/inventory/orders/{id}/complete` (Bestand erhöhen + Bewegung schreiben), `/inventory/orders/{id}/cancel`.
  - Schemas/OpenAPI: OrderCreate/OrderOut/OrderItemOut ergänzt; Roadmap/TODO aktualisiert (PDF/E-Mail bleiben offen).
- **Ergebnis**
  - Tenants können Bestellungen anlegen, einsehen, erledigen oder stornieren; Abschluss erhöht Bestände und protokolliert Bewegungen.
- **Nächster Schritt**
  - Einstellungen/Firmendaten inkl. Auto-Bestellung/Empfänger umsetzen; Bestell-PDF/E-Mail prüfen und bei Bedarf nachziehen; Customer-Frontend an neue Order-APIs anbinden.

## Schritt 30 – Legacy-Migration Phase 3 (T5 Teil 1: Basis-Einstellungen)
- **Datum/Uhrzeit**: 2026-01-05T21:00:00+00:00
- **Ziel**: Tenant-Einstellungen für Firmendaten und Auto-Bestellung bereitstellen.
- **Was wurde geändert**
  - Neues Modell `TenantSetting` (tenant-scoped, unique pro Tenant) mit Firmendaten, Kontakt/Bestell-E-Mail, Auto-Bestellung (Enabled + Min), Export-Format, Adresse, Telefon.
  - Endpunkte `/inventory/settings` GET/PUT liefern/aktualisieren Settings; Defaults werden bei Erstzugriff angelegt.
  - Schemas/OpenAPI ergänzt (`TenantSettings*`); Roadmap/TODO aktualisiert.
- **Ergebnis**
  - Customer/Admin können Basiseinstellungen pro Tenant verwalten; auto_order-Min und Empfänger sind hinterlegt. Mass Import/Export und Test-E-Mail stehen noch aus.
- **Nächster Schritt**
  - Einstellungen Mass Import/Export + Test-E-Mail ergänzen; Bestell-PDF/E-Mail prüfen; Frontend-Settings-View mit neuen Endpunkten verdrahten.

## Schritt 31 – Legacy-Migration Phase 3 (T5 Teil 2: Mass Import/Export)
- **Datum/Uhrzeit**: 2026-01-05T21:30:00+00:00
- **Ziel**: Legacy-Mass-Import/Export für Artikel in den Einstellungen bereitstellen.
- **Was wurde geändert**
  - Endpunkte `/inventory/settings/export` (Excel mit Legacy-Spalten) und `/inventory/settings/import` (Excel-Upload) ergänzt; Tenant-Scoped.
  - Import aktualisiert/legt Items per SKU/Barcode an, nutzt Kategorie-Namen falls vorhanden; Export befüllt Soll/Min/Bestand/Description.
  - OpenAPI ergänzt (Paths + Schema `MassImportResult`); Roadmap/TODO aktualisiert (Test-E-Mail weiter offen).
- **Ergebnis**
  - Massen-Import/Export aus Legacy-Excel-Dateien möglich; Fehlermeldungen je Zeile werden zurückgegeben.
- **Nächster Schritt**
  - Test-E-Mail/Empfängerfluss und optionale Bestell-PDF/E-Mail ergänzen; Customer-Einstellungen-View an neue Endpunkte anbinden.

## Schritt 32 – Legacy-Migration Phase 3 (T5 Teil 3: Test-E-Mail)
- **Datum/Uhrzeit**: 2026-01-05T21:45:00+00:00
- **Ziel**: Test-E-Mail-Funktion gemäß Legacy-Einstellungen bereitstellen.
- **Was wurde geändert**
  - SMTP-Konfiguration in Settings ergänzt (`SMTP_HOST/PORT/USERNAME/PASSWORD/FROM`).
  - Endpoint `/inventory/settings/test-email` sendet Test-Mail an Zieladresse, nutzt TLS/Login falls konfiguriert; liefert Erfolg/Fehler zurück.
  - OpenAPI-Schemas `TestEmailRequest`/`TestEmailResponse` hinzugefügt; Roadmap/TODO aktualisiert.
- **Ergebnis**
  - Tenants können SMTP-Konfiguration prüfen; Fehler werden zurückgegeben.
- **Nächster Schritt**
  - Bestell-PDF/E-Mail prüfen/ergänzen; Customer-Frontend-Einstellungen an neue Endpunkte anbinden.

## Schritt 33 – Legacy-Migration Phase 3 (T4 Ergänzung: Bestell-E-Mail)
- **Datum/Uhrzeit**: 2026-01-05T22:00:00+00:00
- **Ziel**: E-Mail-Versand für Bestellungen ergänzen.
- **Was wurde geändert**
  - SMTP-Konfiguration an Backend-Settings angeglichen (`SMTP_USER` statt `SMTP_USERNAME`).
  - Endpoint `/inventory/orders/{id}/email` sendet Bestellübersicht an Empfänger (Payload oder Settings `order_email`/`contact_email`), nutzt bestehende SMTP-Konfiguration.
  - OpenAPI/Schemas für OrderEmailRequest/EmailSendResponse ergänzt; TODO/Roadmap angepasst (PDF bleibt offen).
- **Ergebnis**
  - Bestellungen können per E-Mail verschickt werden; fehlende Empfänger oder SMTP-Fehler werden zurückgegeben.
- **Nächster Schritt**
  - Bestell-PDF prüfen/ergänzen; Customer-Frontend-Bestellungen/-Einstellungen an neue Endpunkte anbinden.

## Schritt 34 – Legacy-Migration Phase 3 (T4/T5 Ergänzung: Bestell-PDF + Customer-Anbindung)
- **Datum/Uhrzeit**: 2026-01-05T22:30:00+00:00
- **Ziel**: Bestell-PDF ergänzen und Customer-Frontend an Bestell-/Einstellungs-APIs anbinden.
- **Was wurde geändert**
  - Backend: PDF-Export für Bestellungen (`/inventory/orders/{id}/pdf`) mit Positionen; ReportLab als Dependency.
  - Backend: SMTP-User-Feld harmonisiert (`SMTP_USER`).
  - Frontend: Bestellungen-View zeigt offene/erledigte Bestellungen, bestellwürdige Artikel, Aktionen für Erledigen/Storno, PDF/E-Mail.
  - Frontend: Einstellungen-View nutzt echte Settings (GET/PUT), Export/Import, Test-E-Mail.
  - OpenAPI/Schemas für Order-PDF und OrderEmailRequest/EmailSendResponse ergänzt.
  - TODO/Roadmap aktualisiert (PDF erledigt).
- **Ergebnis**
  - End-to-end Bestellverwaltung inkl. PDF/E-Mail und Customer-Frontend-Bedienung der Settings/Orders; verbleibende offenen Punkte nur Admin-Metadaten.
- **Nächster Schritt**
  - Fehlen noch Admin-Metadaten aus Legacy-Einstellungen (falls benötigt) und Feinschliff Frontend (z. B. Order-Erstellung, weitere Filter).

## Schritt 35 – Legacy-Migration Phase 3 (Settings-Admin-Metadaten + UI-Filter)
- **Datum/Uhrzeit**: 2026-01-05T23:15:00+00:00
- **Ziel**: Fehlende Admin-Metadaten aus Legacy-Einstellungen ergänzen und Customer-UI-Feinschliff (Filter) inkl. Fix des Vite-Fehlers umsetzen.
- **Was wurde geändert**
  - Backend: `TenantSetting` um Ansprechpartner, PLZ, Ort, Filialnummer, Steuernummer erweitert; GET/PUT-Ausgabe angepasst, Defaults ergänzt.
  - OpenAPI regeneriert und Customer-API-Typen erneuert.
  - Frontend Einstellungen: Syntaxfehler behoben (`reactive`-Generic), zusätzliche Felder für Admin-Metadaten ergänzt.
  - Frontend Bestellungen: Status-/Suchfilter und Storno-Tabelle ergänzt; PDF-Download nutzt Bestellnummer im Dateinamen.
- **Ergebnis**
  - Legacy-Admin-Metadaten sind abbildbar; UI-Filter/Cancelled-Übersicht vorhanden; Vite-Build-Fehler behoben.
- **Nächster Schritt**
  - DB-Backfill/Migration für neue Settings-Felder prüfen; Responsive/Tokens-Feinschliff fortführen.

## Schritt 36 – Legacy-Migration Phase 3 (Alembic-Revision Settings-Metadaten)
- **Datum/Uhrzeit**: 2026-01-05T23:40:00+00:00
- **Ziel**: DB-Migration für neue Settings-Felder bereitstellen.
- **Was wurde geändert**
  - Alembic-Revision `0008_tenant_settings_metadata` ergänzt, die die neuen Felder (Ansprechpartner, PLZ, Ort, Filialnummer, Steuernummer) anlegt.
  - TODO/Roadmap entsprechend aktualisiert (Rollout-Hinweis, Backfill bei Bedarf).
- **Ergebnis**
  - Migration steht bereit für Rollout; Backend/Frontend nutzen die Felder bereits.
- **Nächster Schritt**
  - Migration in allen Umgebungen ausführen; Backfill je Tenant nach Bedarf; Frontend-Feinschliff (Tokens/Responsive) fortsetzen.

## Schritt 37 – Legacy-Migration Phase 3 (Customer Dashboard an echte Daten anschließen)
- **Datum/Uhrzeit**: 2026-01-06T00:10:00+00:00
- **Ziel**: Customer-Dashboard von Dummywerten befreien und mit Live-Daten aus Backend-APIs speisen.
- **Was wurde geändert**
  - Neue Dashboard-Logik liest offene Bestellungen (`/inventory/orders`), bestellwürdige Artikel (`/inventory/orders/recommended`), Bewegungen des Tages (`/inventory/movements?start=...`) sowie Item-Bestände (alle Seiten) zur Berechnung der Kennzahlen.
  - API-Wrapper ergänzt (`fetchMovements`) zur Abfrage der Bewegungen mit Filter.
  - UI zeigt echte Kennzahlen inkl. Stabilitätsquote (Items >= Mindestbestand), Bewegungen heute und bestellwürdige Artikel; Refresh-Button nutzt Live-Ladevorgang.
- **Ergebnis**
  - Dashboard verwendet keine Dummy-KPIs mehr, sondern aktuelle Daten je Tenant.
- **Nächster Schritt**
  - Responsive/Token-Feinschliff bleibt offen; Migration `0008` ausrollen.

## Schritt 38 – Legacy-Migration Phase 3 (Fix Migration 0008 Tenant Settings)
- **Datum/Uhrzeit**: 2026-01-06T00:25:00+00:00
- **Ziel**: Migration `0008_tenant_settings_metadata` robust machen, falls `tenant_settings` noch nicht existiert.
- **Was wurde geändert**
  - Migration erstellt `tenant_settings` vollständig, falls die Tabelle fehlt (inkl. Unique-Constraint/Index), und fügt andernfalls nur die neuen Metadaten-Spalten hinzu.
  - Server-Defaults werden nach Anlage entfernt, um App-Defaults zu nutzen; numerische Defaults über `sa.text` abgebildet, damit Postgres/Asyncpg sie akzeptiert.
- **Ergebnis**
  - Alembic-Upgrade läuft auch auf Umgebungen ohne vorgenerierte Settings-Tabelle durch.
- **Nächster Schritt**
  - Migration erneut ausrollen; danach optional Backfill der neuen Felder je Tenant prüfen.

## Schritt 39 – Admin: Kunden-Settings bearbeiten & Customer-Settings UI aufräumen
- **Datum/Uhrzeit**: 2026-01-06T01:00:00+00:00
- **Ziel**: Kunden-Adressdaten im Admin-Portal einseh- und bearbeitbar machen sowie Customer-Einstellungen-Formular ordnen.
- **Was wurde geändert**
  - Backend: Admin-Endpunkte `/admin/tenants/{tenant_id}/settings` (GET/PUT) hinzugefügt, nutzen TenantSettings-Modelle.
  - OpenAPI regeneriert und Frontend-Typen neu generiert.
  - Admin-Frontend (Kunden): Detailbereich lädt Tenant-Settings, zeigt Firmendaten/Adresse und erlaubt Speichern.
  - Customer-Frontend (Einstellungen): Formularfelder neu gruppiert (Kontakt/Adresse/Auto-Bestellung) für bessere Übersicht.
- **Ergebnis**
  - Admin kann Kunden-Firmendaten/Adresse einsehen und ändern; Customer-Settings-View wirkt geordneter.
- **Nächster Schritt**
  - Migration ausrollen; Backend-APIs in Zielumgebung prüfen (500/404 laut Screenshot) und Datenbasis/mappings validieren.

## Schritt 40 – Customer UI Feinschliff (Inputs, Dashboard-KPIs, Berichte, Bestellungen)
- **Datum/Uhrzeit**: 2026-01-06T01:38:22Z
- **Ziel**: Dark-Mode-Eingaben aufhellen, Dashboard-KPIs klickbar machen, Reporting-Filter verbessern und Bestell-Workflow tabellarisch mit Bestellwürdig-Autofill abbilden.
- **Was wurde geändert**
  - Tokens um Input-spezifische Variablen ergänzt und globale Styles/PrimeVue-Overrides angepasst, damit Dark-Mode-Inputs heller, mit klarerer Border/Placeholder/Focus erscheinen.
  - Dashboard-KPI-Karten als klickbare Router-Links umgesetzt (`/bestellungen`, `/lagerbewegungen`, `bestellwuerdig`-Tab).
  - Berichte-Filter mit debounce+Abort für Artikelsuche, freundlicher Fehlerbehandlung und Kategorie-abhängigen Vorschlägen ausgestattet; API-Wrapper `fetchItems` akzeptiert `signal`.
  - Bestellungen-View: Neue-Bestellung-Bereich als Tabelle mit Zeilen für Artikel/Menge/Notiz, Bestellwürdig-Preselect, Zeilen hinzufügen/entfernen und per-Item-Notizen; Order-Payload nutzt tabellarischen Zustand.
- **Ergebnis**
  - Dark-Mode-Formulare und PrimeVue-Inputs sind besser lesbar, KPIs navigierbar, Report-Filter performanter nutzbar, Bestellprozess unterstützt Mehrfachauswahl und automatische Übernahme bestellwürdiger Artikel.
- **Nächster Schritt**
  - Im UI verifizieren, dass Dark-Mode-Token-Anpassungen zu gewünschter Helligkeit führen und KPI-Navigation den gewünschten Kontext öffnet; optional weitere Chunk-Splitting-Optionen prüfen (Build-Warnung).
- **Tests**
  - `npm run build` (customer_frontend/customer-ui) – erfolgreich, mit Hinweis auf Chunk-Größe.

## Schritt 41 – Reporting-Filter UX nachschärfen (Debounce + Kategorie-Suggest)
- **Datum/Uhrzeit**: 2026-01-06T02:05:00Z
- **Ziel**: Filter im View „Berichte & Analysen“ responsiver machen: Suche mit Debounce/Abort, Kategorieabhängige Vorschläge und sichtbarer Suchstatus.
- **Was wurde geändert**
  - Debounced Artikelsuche verfeinert: Abbruch bestehender Requests, Suchstatus-Flag, und Default-Suggestions je gewählter Kategorie.
  - Kategorie-Wechsel lädt Vorschlagsliste erneut (wenn kein Suchbegriff), Modus „Selektiert“ triggert automatische Kategorie-Suggestions.
  - ReportFilters zeigt Ladezustand beim AutoComplete an.
- **Ergebnis**
  - Live-Suche reagiert schnell, vermeidet Doppel-Requests, nutzt Kategorie-Filter und hält UI ohne rohe Fehlermeldungen.
- **Tests**
  - `npm run build` (customer_frontend/customer-ui) – erfolgreich, Warnung bzgl. Chunk-Größe unverändert.

## Schritt 42 – Analyse Globale Einstellungen & OpenAPI-Abdeckung
- **Datum/Uhrzeit**: 2026-01-06T03:30:00Z
- **Ziel**: Grundlagen für „Globale Einstellungen“ im Admin-Frontend klären (Navigation, Views, API-Verfügbarkeit für globale Artikel/Kategorien/Typen/Branchen sowie Branchen-Mapping und Tenant-Branchenfeld).
- **Was wurde geprüft**
  - Navigation/Layout: `src/App.vue` zeigt einen statischen Block „Globale Einstellungen“ (Globale Artikel/Kategorien/Typen/Branchen), aber keine klickbaren Routen oder Views; aktive Sektionen sind nur `kunden`, `memberships`, `operations`, `users`, `settings`.
  - Vorhandene Admin-API-Wrapper: `src/api/admin.ts` (Tenants, Users, Memberships, Audit, Diagnostics, Tenant-Settings), `src/api/platform.ts` (Health); beide nutzen die zentrale Axios-Instanz `src/api/client.ts` mit `/api`-Basis.
  - OpenAPI (Admin-Frontend `src/api/gen/openapi.ts`): Inventar-Endpunkte vorhanden für Kategorien (`/inventory/categories` GET/POST, `/inventory/categories/{id}` PATCH) mit Schemata `CategoryCreate/Out/Update` (Name, is_active), Items (`/inventory/items` GET/POST, `/inventory/items/{id}` PATCH, SKU-Existenz, Import/Export) mit `ItemCreate/Update/Out` (SKU/Barcode/Name/Description/Quantity/Unit/is_active/category_id/...); Reporting/Orders/Settings/Movements ebenfalls enthalten.
  - OpenAPI-Lücken: Keine Pfade/Schemata für globale Typen oder Branchen/Industries, kein Mapping Branche↔Artikel, kein Feld für Branche/Industry im `TenantSettings*`-Schema oder in `TenantUpdate`.
- **Ergebnis**
  - Für die geplanten Global-Views existieren nur Inventar-Kategorien/Items-Endpunkte; Typen/Branchen und Mapping sowie ein Tenant-Branchenfeld fehlen im OpenAPI. Navigation/Views für „Globale Einstellungen“ müssen neu aufgebaut werden; fehlende Endpunkte sind zu berücksichtigen (UI+TODO).

## Schritt 43 – Globale Einstellungen UI (UI-only mangels Backend)
- **Datum/Uhrzeit**: 2026-01-06T04:30:00Z
- **Ziel**: Admin-Frontend um bedienbare „Globale Einstellungen“ erweitern (Artikel, Kategorien, Typen, Branchen inkl. Mapping) und Kundenbranche-Dropdown im Tenant-Formular ergänzen, trotz fehlender Backend-Endpunkte.
- **Was wurde geändert**
  - Neue zentrale Stammdaten-Composable `useGlobalMasterdata` mit geteiltem lokalem Zustand (Artikel, Kategorien, Typen, Branchen, Branchen→Artikel-Zuordnung) und ID-Helper; neue API-Wrapper `src/api/globals.ts` für vorhandene Inventar-Pfade (Categories/Items) auf Basis der OpenAPI-Typen.
  - Navigation erweitert: Sidebar-Buttons und Routing für `globals-articles/-categories/-types/-industries`; `App.vue` rendert entsprechende Views mit Titeln/Breadcrumbs.
  - Neue Views `GlobaleArtikelView`, `GlobaleKategorienView`, `GlobaleTypenView`, `GlobaleBranchenView`: jeweils Page/Section-Layout, Suche/Filter, Tabellen, Create/Edit-Dialoge, Status-Tags und Toasts. Mangels Backend sind alle Aktionen UI-only; Hinweise und Disabled-Reloads verdeutlichen fehlende Endpunkte. Branchen-View enthält UI-only Mapping Branche→Artikel (Checkbox-Multiselect).
  - Tenant-Formular: Dropdown „Kundenbranche (UI-only)“ mit globalen Branchen aus dem gemeinsamen Zustand; Auswahl wird pro Tenant in `localStorage` gepuffert, da `TenantSettings` kein Branchenfeld bietet. Kein Einfluss auf Payload.
  - TODO/Roadmap aktualisiert: fehlende Backend-Endpunkte für globale Stammdaten und Branchenfeld in Tenant-Settings dokumentiert.
- **Tests**
  - `npm run build` (admin_frontend/admin-ui)

## Schritt 46 – Admin Settings Analyse & Planung
- **Datum/Uhrzeit**: 2026-01-06T11:08:24+00:00
- **Ziel**: Ist-Zustand der Admin-Settings-View erfassen, API-Aufrufe und Blöcke dokumentieren, Plan für Refactor anlegen.
- **Was wurde geprüft**
  - Settings-View (`src/views/AdminSettingsView.vue`) enthält einen einzigen Card-Block mit KV-Rastern für Systeminfos (API Base, Base Domain, Observability-Link auf `VITE_GRAFANA_URL`), Admin-Key-Länge, Actor-Anzeige, Theme-Toggle (radio, emit `setTheme`), Admin-Context-Reset-Button sowie Security/Feature-Flag-Hinweise.
  - Enthält „User Management (Quick)“-Sektion mit Create/Passwort/Status-Änderung; lädt Nutzer per `adminListUsers`, nutzt `adminCreateUser` und `adminUpdateUser` (Passwort/Active-Flag). `loadUsers` wird `onMounted` getriggert, bricht ohne Admin-Key ab.
  - Weitere API-Aufrufe in Settings gibt es nicht; keine System-Action-Endpunkte (Cache reset/Reindex) im Admin-Frontend gefunden.
  - Admin-Navigation (`src/App.vue`) hat dedizierte Benutzer-View (`AdminUsersView.vue`) mit vollständigem User-Management (Listen/Filter/Status/Passwort/CSV-Export).
- **Ergebnis**
  - Quick-User-Management gehört in die Benutzer-View und macht die Settings unklar; Settings-Inhalte müssen in System/Security/Theme/Flags/Danger-Zone gegliedert werden. Roadmap-Eintrag und TODO ergänzt.
- **Offene Punkte**
  - Danger-Zone-Aktionen fehlen als Endpunkte/Buttons; bei Refactor nur Hinweis/Platzhalter möglich, Backend-Klärung nötig.

## Schritt 47 – Admin Settings restrukturiert & User-Quick-Actions verlagert
- **Datum/Uhrzeit**: 2026-01-06T11:15:05+00:00
- **Ziel**: Settings-Seite auf System/Security/Theme/Flags/Danger-Zone fokussieren und User-Management-Formulare in die Benutzer-Ansicht verschieben.
- **Was wurde geändert**
  - `AdminSettingsView.vue` in Abschnitte gegliedert (System mit Health-Anzeige, Security & Auth, Theme & UI, Feature Flags, Danger Zone). User-Management-Blöcke entfernt; Danger-Zone nur als Hinweis, da keine Endpunkte vorhanden.
  - Neue Komponente `UserQuickActions.vue` mit bisherigem Quick-User-Management (Anlegen, Passwort setzen, Status) unter `components/users/`.
  - `AdminUsersView.vue` bindet Quick-Actions ein, synchronisiert Auswahl/Liste und nutzt gemeinsame Update-Helfer.
  - Roadmap aktualisiert; TODO bereinigt.
- **Ergebnis**
  - Settings zeigen nur noch systemweite, seltene Konfigurationen; User-Operationen liegen konsistent im Menüpunkt „Benutzer“. Danger-Zone weist auf fehlende System-Action-Endpunkte hin.
- **Tests**
  - `npm run build` (admin_frontend/admin-ui)

## Schritt 44 – Admin Globales: Einheiten & Import/Export Hinweis
- **Datum/Uhrzeit**: 2026-01-06T05:20:00Z
- **Ziel**: Korrektur „Globale Typen“ → „Globale Einheiten“, Import/Export-Anforderungen sichtbar machen und Backend-Lücken dokumentieren (admin-fähige Artikel-Import/Export-Endpunkte, Einheiten, Schreibschutz/Prefix-Regel für Kundenartikel).
- **Was wurde geändert**
  - Neue View `GlobaleEinheitenView` (UI-only mangels Endpunkte) und Navigation/Title angepasst; bestehende Typen-View entfernt.
  - Artikel-View ergänzt um Import/Export-Sektion mit deaktivierten Aktionen und Hinweisen auf fehlende Admin-Endpunkte; Hinweise auf Schreibschutz für Admin-Artikel und `z_`-Prefix für Kundenartikel aufgenommen.
  - Globals-Composable um Einheiten-State ergänzt; Artikel-Form nutzt globale Einheiten (Fallback auf Standardwerte).
  - TODO/Roadmap erweitert um benötigte Backend-Endpunkte (Admin-Import/Export, Einheiten, Schreibschutz/Prefix).
- **Tests**
  - `npm run build` (admin_frontend/admin-ui)

## Schritt 45 – OpenAPI aktualisiert (lokale Generierung, Konfliktarme Struktur)
- **Datum/Uhrzeit**: 2026-01-06T05:50:00Z
- **Ziel**: Defekte/inkonsistente `docs/openapi/openapi.json` reparieren und OpenAPI-Typen neu generieren, damit Codex ohne Merge-Konflikt-fördernde Manuelleingriffe arbeiten kann.
- **Was wurde geändert**
  - `docs/openapi/openapi.json` frisch per FastAPI `get_openapi` mit Dummy-ENV (ohne DB-Init) generiert; fehlerhafte Blöcke (Order E-Mail/PDF) damit bereinigt.
  - `npm run gen:types` im Admin-Frontend ausgeführt, damit `src/api/gen/openapi.ts` zur neuen Spec passt (inkl. `/inventory/units` etc.).
  - Build erneut ausgeführt, um Typkompatibilität sicherzustellen.
- **Tests**
  - `npm run build` (admin_frontend/admin-ui)
