# EPIC A – Tenant-Auflösung & Fehler-UX (Frontend-gesteuert)

## 1) Ziel
Frontend zeigt für unbekannte/inaktive Subdomains eine klare Seite statt JSON. Tenant-Status wird vor App-Bootstrap geprüft.

## 2) Problem heute
- Backend liefert bei fehlendem oder inaktivem Tenant 404 mit JSON (`tenant_not_found`).
- Customer-Router hat keine Not-Found-Route; Browser zeigt leere Seite oder rohes JSON.
- Reverse-Proxy erwartet Subdomain + `X-Forwarded-Host`; fehlende Headers führen zu JSON-Fehlern.

## 3) Scope
- Customer-Frontend steuert die Tenant-Status-Seite und das Routing.
- Minimaler öffentlicher Endpoint für Tenant-Status.
- Admin-Frontend bleibt unverändert (kein Tenant-Kontext).

## 4) Nicht-Ziele
- Keine Backend-Umbauten für Auth/Inventory-Logik.
- Keine neuen Proxy-Setups; nur Header-Nutzung dokumentieren.
- Keine automatische Tenant-Neuanlage.

## 5) User Journeys
- User öffnet `tenantX.domain`; Frontend ruft `GET /api/public/tenant-status?slug=tenantX` vor App-Init.
- Zustand "not found/inactive": Landing mit Hinweis und CTA (zurück zu Hauptseite/Support kontaktieren).
- Zustand "service unavailable": Hinweis mit Retry-Button.
- Zustand "ok": regulärer App-Start und Login.

## 6) UI/UX Regeln
- Vier States: Tenant not found, Tenant inactive, Service unavailable, Unknown path (404). Jeder mit Klartext, Support-Hinweis, optional Host-Anzeige.
- Keine rohen Statuscodes im sichtbaren Text; technische Details einklappbar.
- CTA-Pattern: Primär "Zurück zur Startseite" oder "Support kontaktieren", Sekundär "Erneut versuchen".

### A-05 Tenant-Status-View – Copy & Layout (Entwurf)
**Layout-Bausteine**
- Icon/Illustration (neutral, nicht alarmierend).
- Titel + Kurztext (max. 2 Sätze).
- Aktionen (Primary/Secondary).
- Support-Block (E-Mail/Telefon/Link).
- Technische Details (optional einklappbar: `host`, `slug`, `status`, `reason`).

**States & Texte**
- **Tenant not found**
  - Titel: „Mandant nicht gefunden“
  - Text: „Für diese Adresse ist kein Mandant hinterlegt. Prüfe die URL oder kontaktiere den Support.“
  - Primary: „Zur Startseite“ → Root ohne Subdomain
  - Secondary: „Support kontaktieren“
- **Tenant inactive**
  - Titel: „Mandant inaktiv“
  - Text: „Dieser Mandant ist derzeit deaktiviert. Bitte wende dich an den Support.“
  - Primary: „Support kontaktieren“
  - Secondary: „Erneut versuchen“
- **Service unavailable**
  - Titel: „Service nicht verfügbar“
  - Text: „Der Dienst ist gerade nicht erreichbar. Bitte versuche es in wenigen Minuten erneut.“
  - Primary: „Erneut versuchen“
  - Secondary: „Status prüfen“ (optional, falls Statusseite existiert)
- **Unknown path (404)**
  - Titel: „Seite nicht gefunden“
  - Text: „Diese Seite gibt es nicht. Wechsle zur Startseite oder suche im Menü.“
  - Primary: „Zur Startseite“
  - Secondary: „Support kontaktieren“

## 7) API/Backend Annahmen
- Neuer öffentlicher Endpoint `GET /api/public/tenant-status?slug=` liefert `{status: ok|not_found|inactive|unavailable, host, slug}`.
- Bestehende Tenant-Resolve-Logik bleibt; Status-Endpoint nutzt dieselbe Prüfung ohne Login.
- Proxy leitet Subdomain-Host in `X-Forwarded-Host` weiter.
- Spezifikation: `docs/openapi/TENANT_STATUS.md`, Schema `PublicTenantStatus` in `docs/openapi/openapi.json` (Typen via `npm run gen:types(:local)`).

## 8) Daten (konzeptionell)
- Response `tenant-status`: `status` Enum, `slug`, `host`, optional `reason`/`is_active`.
- Frontend-Store für Tenant-Metatate (Status, letzte Prüfung, Host).

## 9) Tasks (umsetzbar, klein)
- **A-01** – Tenant-Status-API spezifizieren (`/api/public/tenant-status` Response/Fehlercodes).  
  - Bereich: backend/docs  
  - Dateien/Bereiche: docs/openapi, Backend-Router `modules/auth` oder neuer public-Router  
  - Abhängigkeiten: keine  
  - Done: Spezifikation ergänzt, Testszenarien beschrieben.
- **A-02** – Public-Router anlegen mit `tenant-status` Endpoint (ohne Auth).  
  - Bereich: backend  
  - Dateien/Bereiche: neuer Router `modules/public/routes.py`, main-Router include  
  - Abhängigkeiten: A-01  
  - Done: Endpoint liefert Status ok/not_found/inactive/unavailable.
- **A-03** – Tenant-Resolver nutzen, aber JSON-Fehler auf kompaktes Statusschema mappen.  
  - Bereich: backend  
  - Dateien/Bereiche: core/tenant.py, public endpoint  
  - Abhängigkeiten: A-02  
  - Done: Fehlende/Inactive Tenants liefern `status: not_found|inactive` ohne Traceback.
- **A-04** – Customer-Bootstrap: Preflight-Check vor Router-Init (Status-Fetch).  
  - Bereich: customer  
  - Dateien/Bereiche: `src/main.ts`, `src/composables`  
  - Abhängigkeiten: A-02  
  - Done: App startet nur bei `status=ok`.
- **A-05** – Tenant-Status-View für Not-Found/Inaktiv/Unavailable gestalten (ohne Login).  
  - Bereich: customer  
  - Dateien/Bereiche: `src/views/TenantStatusView.vue`, `src/router/index.ts`  
  - Abhängigkeiten: A-04  
  - Done: State-spezifische Texte + Aktionen sichtbar.
- **A-06** – Router-Fallback `/:pathMatch(.*)*` auf Tenant-Status/404 führen.  
  - Bereich: customer  
  - Dateien/Bereiche: `src/router/index.ts`  
  - Abhängigkeiten: A-05  
  - Done: Unbekannte Pfade zeigen 404-Ansicht ohne JSON.
- **A-07** – UX-Kopien und CTA-Links (Support, Zurück) definieren.  
  - Bereich: docs/customer  
  - Dateien/Bereiche: neue UX-Kopie-Sektion in Epic/Docs  
  - Abhängigkeiten: A-05  
  - Done: Texte abgestimmt, Links dokumentiert.
- **A-08** – Status-Caching/Retry-Strategie implementieren (Backoff, Cache 5min).  
  - Bereich: customer  
  - Dateien/Bereiche: `src/composables`, `src/utils`  
  - Abhängigkeiten: A-04  
  - Done: Mehrfachaufrufe vermeiden, Retry-Button funktionsfähig.
- **A-09** – Telemetrie/Logging für Tenant-Fehler (optional, Konsole/Endpoint).  
  - Bereich: customer/backend  
  - Dateien/Bereiche: Logging-Hook im Frontend, optional Backend metrics  
  - Abhängigkeiten: A-02, A-04  
  - Done: Fehler werden gezählt/geloggt ohne PII.
- **A-10** – QA-Checkliste (States, Mobile, Darkmode) dokumentieren.  
  - Bereich: docs  
  - Dateien/Bereiche: Epic QA-Abschnitt, README QA  
  - Abhängigkeiten: A-05  
  - Done: Checkliste in Doku, deckt 404-Fallback, Tenant not found/inaktiv/unavailable, Header-Szenarien, Mobile/Darkmode, Proxy-Forwarding.
- **A-11** – Proxy/404 Smoke-Test-Plan erstellen (Reverse Proxy Verhalten).  
  - Bereich: docs/devops  
  - Dateien/Bereiche: Epic QA-Abschnitt, ggf. `docs/` Test-Notiz  
  - Abhängigkeiten: A-10  
  - Done: Plan beschreibt Aufrufpfade (mit/ohne Subdomain, falsche Slugs), erwartete Responses (UI-Seite statt JSON), benötigte Proxy-Header (`X-Forwarded-Host`), und manuelle Schritte.

## QA-Checkliste (A-10)
- 404-Fallback: Route `/:pathMatch(.*)*` führt zu TenantStatusView, kein rohes JSON.
- Tenant not found: Subdomain/Slug unbekannt → UI-Text + Aktionen (Retry, Startseite/Support).
- Tenant inactive: Inaktive Tenant-DB-Flag → UI-Text + Aktionen, keine JSON-Fehler sichtbar.
- Service unavailable: DB down oder Timeout → UI-Text mit Grund, Retry-Button funktioniert.
- Header-Szenarien: Mit/ohne `X-Forwarded-Host`, mit/ohne `X-Tenant-Slug`; Status-API liefert konsistenten Status (siehe Proxy-Header-Matrix in `docs/openapi/TENANT_STATUS.md`).
- Mobile/Darkmode: TenantStatusView bleibt lesbar/bedienbar, Actions/Links erreichbar.
- Proxy: Weitergeleitete Hosts ohne Subdomain zeigen „not_found“ und kein Stacktrace/JSON.

## 10) Akzeptanzkriterien
- Unbekannte/Inactive Tenant-Subdomain zeigt eine gestaltete Seite, kein JSON.
- Router-Fallback zeigt 404-Seite, nicht leere Shell.
- Tenant-Status-API antwortet ohne Auth mit Status ok/not_found/inactive/unavailable.
- Tenant-Status-API liefert für alle Pfade HTTP 200, Fehlerzustände liegen ausschließlich in `status`/`reason`.
- Retry/Support-Links funktionieren; Host/Tenant-Slug im UI sichtbar.
- QA-Checkliste A-10 ist vorhanden und getestet (404-Fallback, Tenant not found/inaktiv/unavailable, Proxy-Header, Mobile, Darkmode).

## 11) Risiken/Offene Punkte
- Proxy muss `X-Forwarded-Host` korrekt setzen; sonst falscher Tenant.
- Cache/Retry darf Login-Fluss nicht blockieren.
- Service-unavailable-Definition (z. B. DB down) muss im Backend sauber erkannt werden.
