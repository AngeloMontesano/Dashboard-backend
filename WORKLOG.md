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

## 2024-06-16
- Vorbereitung Umsetzung: Startpunkte für Coding geklärt (Stream 1: A-01 Spezifikation finalisieren → Backend-Stub; Stream 2: A-04 Bootstrap-Check + C-02/D-01 UX-Flow; Stream 3: G-01/I-01 Doku-/Felddesign).
- Keine neuen Blocker; nächste Schritte sind Kickoff der Stream-Arbeiten.

## 2024-06-17
- Parallelisierung für Next/Later ergänzt (TODO): Stream 1 (A-05/A-10/B-02), Stream 2 (C-03/C-04/D-02), Stream 3 (E-03/E-04/E-05/F-04/F-05).
- Ziel: spätere Tasks früh bündeln, um Reviews/UX-Guidelines gemeinsam zu nutzen.

## 2024-06-18
- Umsetzungsvorbereitung konkretisiert: Stream 1 startet mit A-01 Draft in `docs/openapi` + Backend-Router-Stubs; Stream 2 legt UX-Wireframes für A-04/C-02/D-01 an; Stream 3 entwirft Felder/Abschnitte für G-01/I-01.
- Keine neuen Blocker; offene QA-Themen (Proxy-404) bleiben offen, erst nach A-10/A-11 anpacken.

## 2024-06-19
- TODO ergänzt um klare Deliverables pro Stream (Now): Stream 1 Draft-Specs/Monitoring-Notiz, Stream 2 Wireframes/Flow-Diagramme, Stream 3 IA und Feldtabellen.
- Ziel: ersten Artefakte je Stream vorziehen, um danach Coding zu starten; keine neuen Blocker.

## 2024-06-20
- Draft für A-01 erstellt: `docs/openapi/TENANT_STATUS.md` beschreibt Request/Response, Header-Reihenfolge, Reason-Codes und OpenAPI-Schema-Referenz.
- EPIC_A ergänzt (API/Backend-Annahmen) um Verweis auf das neue Spec-Dokument; TODO-Deliverables (Stream 1) aktualisiert.
- Offene Punkte: Review/Abnahme A-01-Spec; Proxy-404-Tests (A-11) weiterhin offen, QA-Checkliste (A-10) noch umzusetzen.

## 2024-06-21
- Roadmap-Index um Spezifikations-Links ergänzt (TENANT_STATUS.md + openapi.json), damit A-01-Referenz zentral auffindbar ist.
- Keine Änderungen an Tasks; Fokus bleibt auf Review der A-01-Spec und nachgelagerter QA (A-10/A-11).
- Offene Punkte unverändert: A-01 Review, Proxy-404-Szenarien testen.

## 2024-06-22
- TENANT_STATUS-Spec erweitert um cURL-Beispiele, QA-Hinweise (A-10/A-11) und Fehlersimulation (DB down → unavailable).
- Ziel: schnelleres Review von A-01 und klare Prüfschritte für Header-/Slug-Varianten; keine Task-IDs geändert.
- Offene Punkte: Review/Abnahme A-01; danach QA-Checkliste (A-10) und Proxy-Szenarien (A-11) ausführen.

## 2024-06-23
- TENANT_STATUS-Spec um HTTP-Status-Hinweis (immer 200), Review-Checkliste und Klarstellung der Header-Priorität ergänzt.
- Fokus: A-01 Review beschleunigen; QA/Proxy Tasks (A-10/A-11) weiterhin offen, keine Task-IDs angepasst.
- Offene Punkte unverändert: A-01 Abnahme, danach QA-Checkliste und Proxy-Testplan ausführen.

## 2024-06-24
- EPIC_A Akzeptanzkriterien ergänzt: Tenant-Status-API liefert immer HTTP 200, Fehler nur im Feld `status/reason`.
- Ziel: Review von A-01 vereinfachen und klar gegen A-10/A-11 abgrenzen; keine Task-IDs geändert.
- Offene Punkte: A-01 Abnahme; danach QA-Checkliste (A-10) und Proxy-Tests (A-11) ausführen.
