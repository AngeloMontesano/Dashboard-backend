# WORKLOG

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
