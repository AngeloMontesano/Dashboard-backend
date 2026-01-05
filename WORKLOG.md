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
