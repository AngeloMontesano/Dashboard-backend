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
- EPIC_B Spezifikation `docs/openapi/GLOBAL_CATALOG.md` erweitert: Paging-Metadaten in Listen, zusätzliche Fehlercodes (`industry_in_use/category_in_use/item_in_use/forbidden_system_record`), cURL-Beispiele und QA-Checkliste.
- Ziel: B-02 Review und anschließender Alembic-Entwurf (B-03) beschleunigen; keine neuen Tasks oder ID-Anpassungen.

## 2024-06-29
- Roadmap-Index verlinkt GLOBAL_CATALOG-Spezifikation; EPIC_B ergänzt um Paging-/Fehlercode-Annahmen und Akzeptanzkriterium.
- Ziel: B-02/B-03 Reviewer haben zentrale Referenzen; keine Task-IDs geändert.
- Status-Codes und Paging-Limits in GLOBAL_CATALOG.md dokumentiert; offene Punkte: B-01/B-02 Review, Schemas in openapi.json nachziehen, danach B-03/B-04.

## 2024-06-30
- GLOBAL_CATALOG.md ergänzt um Headerpflicht (`X-Admin-Key`, optional `X-Admin-Actor`) und Response-Envelope-Hinweis (kein zusätzliches `data`, Listen mit `{total, limit, offset}`); EPIC_B/Index entsprechend angepasst.
- Ziel: Header-/Envelope-Kontrakt für B-02/B-03 festziehen; Tasks unverändert, offene Punkte bleiben Schema-Sync in openapi.json und Start B-03/B-04.

## 2024-07-01
- EPIC_B Akzeptanzkriterium präzisiert (Headerpflicht, nackte Ressourcen ohne `data`-Wrapper); Roadmap-Index verweist auf den Envelope-Hinweis.
- Ziel: Reviewer können Header-/Envelope-Pflicht direkt im Epic nachvollziehen; Tasks bleiben gleich, offene Punkte: Schema-Sync in openapi.json, danach B-03/B-04.

## 2024-07-02
- EPIC_F um Komponentenstruktur (F-04) ergänzt; EPIC_G Help-Button Konzept Customer (G-05) konkretisiert; EPIC_H Deploy-Snippet ohne Grafana (H-04) ergänzt.
- Ziel: mehrere Next-Tasks parallel dokumentiert, ohne Implementierung; Tasks unverändert.

## 2024-07-03
- EPIC_C Live-Suche (C-03) um Datenformate/States/A11y ergänzt; EPIC_D Router-Prefill-Interface (D-02) beschrieben; EPIC_E Dialog-Komponente (E-03) skizziert.
- Ziel: mehrere Next-Tasks parallel konkretisiert; keine Task-IDs geändert.

## 2026-01-07
- EPIC_A A-05 Tenant-Status-View erweitert: Layout-Bausteine, States, CTAs, Support-Block.
- EPIC_I I-04 Admin-UI Formulare für globale Kontakte konkretisiert (Felder, Validierung, Save-Verhalten).
- EPIC_C C-04 Mehrfachauswahl (Chips, Limits, States) beschrieben.
- EPIC_E E-04 Validierungsregeln für Bestell-Dialog ergänzt.
- EPIC_C C-05 Zeitraum-Presets (Presets/Custom/Limit) dokumentiert.
- EPIC_E E-05 Fehlerdarstellung ohne rote Ränder definiert.
- EPIC_B B-02 Schema-Sync in `docs/openapi/openapi.json` ergänzt (Global Categories/Types/Industries).
- Ziel: Phase 1 abgeschlossen; Next-Tasks dokumentiert, keine Task-IDs geändert.
- EPIC_B B-03 Alembic-Entwurf: globale Typen-Tabelle + Item-Relation ergänzt (Migration + Model).
- EPIC_B B-04 Admin-UI: Navigationspunkt „Globale Kataloge“ mit Übersichts-View ergänzt.
- EPIC_B B-05 Admin-UI: Navigationspunkt für bestehende „Globale Typen“-View ergänzt (UI-only).
- EPIC_B B-05 Admin-UI: Global-Types-State im Masterdata-Store ergänzt (UI-only).
- EPIC_B B-05 Backend/Frontend: Admin-API für globale Typen ergänzt und View angebunden.
- EPIC_B B-05 Admin-UI: Globale Artikel um Typ-Filter/Anzeige erweitert (type_id).
