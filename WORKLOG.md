## 2024-06-08
- Standards aus `docs/standards/` gelesen und nicht verhandelbare Regeln im Roadmap-Index verdichtet.
- Frontend-Scan: Customer-Router (`customer_frontend/customer-ui/src/router/index.ts`) besitzt Fallback `/:pathMatch(.*)*` auf `TenantStatusView`; Admin-UI arbeitet ohne Router (Single-Shell). Tenant-Status-View zeigt Statusseiten statt JSON, 404-Route nutzt dieselbe View.
- Backend-Scan: Tenant-Resolution in `app/core/tenant.py` wirft 404 JSON (`tenant_not_found`) bei fehlendem oder inaktivem Tenant; Public Endpoint `/public/tenant-status` liefert Status ok/not_found/inactive/unavailable; Fehler-Responses vereinheitlicht über `app/core/errors.py` (JSON mit `error.code/message`). Reverse-Proxy-Annahme: `X-Forwarded-Host` bzw. Subdomain vor `BASE_DOMAIN`, Fallback `localhost`.
- Bestandsaufnahme 404/Not-Found: Customer-Frontend 404 führt zu TenantStatusView (kein blank JSON), Backend liefert JSON-Fehler mit Codes, Proxy-seitig keine dedizierte 404-Seite (abhängig von Forwarding, sonst Backend-JSON).
- JSON-Fehler im Browser: bei fehlendem Tenant oder Backend-404 erscheinen strukturierte JSON-Fehler (`{"error":{"code":"tenant_not_found",...}}`) aus FastAPI, sofern nicht durch TenantStatusView abgefangen.
- Geänderte/erstellte Dateien: `docs/roadmap/INDEX.md`, `TODO.md`, `Epic_TODO.md`, `Epic_WORKLOG.md`, `WORKLOG.md`.
- Offene Punkte: QA-Checkliste für Tenant-Status-UX noch ausstehend; Proxy-404-Verhalten nicht getestet (nur Code-Scan).

## 2024-06-09
- Epics gegen Template geprüft, Qualitätscheck-Liste in `docs/roadmap/INDEX.md` ergänzt.
- Konsistenzprüfung TODO/Epic_TODO ↔ Epics/Task-IDs durchgeführt, keine Lücken gefunden.
- Offene Punkte: QA-Checkliste Tenant-Status-UX weiterhin offen; Proxy-404-Verhalten bleibt zu testen.

## 2024-06-10
- Roadmap-Index um Backlog-/Log-Links ergänzt (TODO, Epic_TODO, WORKLOGs) für schnellere Navigation.
- Keine weiteren Befunde zu 404-/JSON-Verhalten; offene Punkte bleiben unverändert.
- Offene Punkte: QA-Checkliste Tenant-Status-UX offen; Proxy-404-Verhalten weiterhin ungetestet.
- Hinweis ergänzt: OpenAPI Single Point of Truth ist `https://api.test.myitnetwork.de/openapi.json`, lokale `docs/openapi/openapi.json` spiegelt den Stand für Typgenerierung.

## 2024-06-11
- Roadmap-Index mit Typgenerierungsbefehlen ergänzt (`npm run gen:types`, `npm run gen:types:local`) und Zielpfad `src/api/gen/openapi.ts` festgehalten.
- Offene Punkte unverändert: QA-Checkliste Tenant-Status-UX, Proxy-404-Verhalten noch zu testen.

## 2024-06-12
- EPIC_A QA-Checkliste konkretisiert (404-Fallback, Tenant not found/inaktiv/unavailable, Proxy-Header, Mobile, Darkmode).
- TODO-Backlog um A-10 (QA-Checkliste Tenant-Status) in „Next“ ergänzt.
- Offene Punkte: Proxy-404-Verhalten weiterhin ungetestet; QA-Checkliste noch umzusetzen.

## 2024-06-13
- QA-Checkliste (A-10) als eigene Section in EPIC_A ergänzt und Szenarien konkretisiert (404-Fallback, Header-Kombinationen, Mobile/Darkmode).
- Offene Punkte bleiben: Proxy-404-Verhalten praktisch testen, QA-Checkliste durcharbeiten.

## 2024-06-14
- EPIC_A um Task A-11 ergänzt (Proxy/404 Smoke-Test-Plan mit Header-Kombinationen und erwarteten UI-States).
- TODO-Liste „Later“ um A-11 erweitert, Umsetzung steht noch aus.
- Epic_TODO um A-11 ergänzt, damit Tasklisten konsistent sind.

## 2024-06-15
- Parallelisierung ergänzt: drei Streams in TODO (Backend/Docs, Customer UX, Admin/Docs) für gleichzeitige Bearbeitung der Now-Tasks.
- Keine neuen fachlichen Findings; Fokus auf Beschleunigung der Planungs-/QA-Arbeiten.
