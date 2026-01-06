## 2024-06-08
- Scope abgeglichen, bestehende Epics geprüft und an Template aus INDEX angepasst.
- TODO-Backlog nach Epics/Tasks neu aufgebaut (Epic_TODO.md, TODO.md).
- Standards aus `docs/standards/` als nicht verhandelbare Regeln im Roadmap-Index verlinkt.

## 2024-06-09
- Qualitätscheck-Sektion im Roadmap-Index ergänzt, um Template-Konformität der Epics abzusichern.
- Konsistenzprüfung der Task-IDs zwischen Epics, TODO.md und Epic_TODO.md durchgeführt (keine Abweichungen gefunden).

## 2024-06-10
- Roadmap-Index um Backlog-/Log-Quellen ergänzt (TODO, Epic_TODO, WORKLOGs) zur schnelleren Referenz je Epic.
- Keine weiteren Anpassungen an Epic-Inhalten nötig; Epics bleiben template-konform.
- OpenAPI Single Point of Truth im Index erwähnt (`https://api.test.myitnetwork.de/openapi.json`) als Referenz für alle API-bezogenen Tasks.

## 2024-06-11
- Typgenerierungsbefehle (remote/local) und Zielpfad `src/api/gen/openapi.ts` im Roadmap-Index ergänzt, damit API-bezogene Epics denselben Workflow nutzen.
- Keine Anpassungen an Epic-Inhalten selbst; nur Navigations-/Referenzupdate.

## 2024-06-12
- EPIC_A um präzisierte QA-Checkliste (A-10) erweitert; Akzeptanzkriterien referenzieren die Checkliste.
- TODO-Backlog spiegelt A-10 jetzt in „Next“ wider.

## 2024-06-13
- QA-Checkliste (A-10) als eigene Section in EPIC_A ergänzt, Szenarien detailliert (404-Fallback, Header-Kombinationen, Mobile/Darkmode).
- Keine Änderungen an anderen Epics; Fokus auf QA-Dokumentation.

## 2024-06-14
- EPIC_A um Task A-11 ergänzt (Proxy/404 Smoke-Test-Plan), Backlog in TODO aktualisiert.
- Epic_TODO ebenfalls mit A-11 ergänzt für Konsistenz der Tasklisten.
- Weitere Epics unverändert.

## 2024-06-20
- A-01 spezifiziert: neues Dokument `docs/openapi/TENANT_STATUS.md` (Request/Response, Header-Priorität, Reason-Codes, OpenAPI-Verweis).
- EPIC_A API/Backend-Annahmen mit Verweis auf Spezifikation ergänzt; TODO-Deliverables (Stream 1) präzisiert.
- Nächste Schritte: Review/Abnahme A-01, danach QA-Checkliste A-10 und Proxy-Tests A-11 vorbereiten.

## 2024-06-21
- Roadmap-Index ergänzt um Spezifikations-Links (TENANT_STATUS.md, openapi.json) zur zentralen Referenz der A-01-Quelle.
- Keine Änderungen an Epic-Tasks; A-01 bleibt im Review, QA/Proxy-Arbeiten (A-10/A-11) folgen danach.

## 2024-06-22
- TENANT_STATUS-Spec präzisiert (cURL-Beispiele, QA-Hinweise für Header/Slug/DB-Down). Keine neuen Tasks, nur Klarstellung für A-01 Review.
- Nächste Schritte: A-01 abnehmen, dann QA-Checkliste (A-10) und Proxy-Testplan (A-11) durchführen.

## 2024-06-23
- TENANT_STATUS-Spec ergänzt (Status immer 200, Review-Checkliste, Header-Priorität). Keine Task-ID-Änderungen.
- Offene Punkte: A-01 Review abschließen; danach QA/Proxy-Aufgaben (A-10/A-11) angehen.

## 2024-06-24
- EPIC_A Akzeptanzkriterium ergänzt: Tenant-Status-API liefert in allen Pfaden HTTP 200, Fehler nur als `status/reason`.
- Keine neuen Tasks; Fokus bleibt auf A-01 Review, anschließend QA/Proxy (A-10/A-11).

## 2024-06-25
- TENANT_STATUS-Spec um Proxy-Header-Matrix ergänzt (Vorbereitung A-11, Host/Slug/DB-down).
- Keine Task-Änderungen; nächste Schritte bleiben A-01 Review, danach QA/Proxy-Checks (A-10/A-11).

## 2024-06-26
- EPIC_A QA-Checkliste verweist jetzt auf Proxy-Header-Matrix in TENANT_STATUS.md, damit A-10/A-11 konsistent prüfen.
- Tasks unverändert; Fokus: A-01 Review, dann QA/Proxy-Checks.

## 2024-06-27
- Roadmap-Index-Referenz für A-01 erwähnt jetzt die Proxy-Header-Matrix (A-11 Vorbereitung) für konsistente QA.
- Keine Task-Änderungen; nächste Schritte unverändert (A-01 Review, dann A-10/A-11).

## 2024-06-28
- TENANT_STATUS-Spec um Implementierungs-Mapping ergänzt (Backend-Router, Slug-Priorität, DB-Probe, 200-only Responses).
- EPIC_A API/Backend-Annahmen mit aktuellem Backend-Stand verknüpft, um Coding-Startpunkte klarer zu machen.
- Offene Punkte: A-01 Review; danach QA-Checkliste (A-10) und Proxy-Smoke-Plan (A-11) ausführen.
