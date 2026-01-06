## EPIC A – Tenant-Auflösung & Fehler-UX
- A-01: Tenant-Status-API spezifizieren (docs/openapi)
- A-02: Public-Router `tenant-status` Endpoint planen
- A-03: Tenant-Resolver-Fehler auf Statusschema mappen
- A-04: Customer-Bootstrap Preflight Tenant-Status
- A-05: Tenant-Status-View Texte/CTAs
- A-06: Router-Fallback 404 → Tenant-Status
- A-07: UX-Kopien/Support-Links definieren
- A-08: Status-Caching/Retry-Strategie
- A-09: Telemetrie/Logging für Tenant-Fehler
- A-10: QA-Checkliste (States/Mobile/Darkmode)

## EPIC B – Globale Kataloge & Branchen
- B-01: Datenmodell-Entwurf globale Tabellen/Keys
- B-02: Admin-API Spezifikationen für Kataloge
- B-03: Alembic-Entwurf für neue Tabellen/Felder
- B-04: Admin-Nav „Globale Kataloge“ anlegen
- B-05: View globale Kategorien/Typen CRUD
- B-06: View globale Artikel inkl. Branche/Typ
- B-07: Branche→Artikel Mapping (Filter/Bulk)
- B-08: Tenant-Detail Branche Dropdown
- B-09: API-Wiring Admin-Client neue Endpoints
- B-10: Konzept Verteilung an Tenants
- B-11: Akzeptanz-Tests definieren

## EPIC C – Customer Reporting UX
- C-01: Filter-API/Parameter validieren
- C-02: UX-Flow Reporting Startseite (Top-5)
- C-03: Live-Suche-Komponente (Prefix/Debounce)
- C-04: Mehrfachauswahl Artikel/Kategorien
- C-05: Zeitraum-Presets + Custom planen
- C-06: Top-5 Default + Override Logik
- C-07: Leere Zustände/Fehlertexte
- C-08: Lade-/Performance-Hinweise
- C-09: Export-Konzept (Button/Format)
- C-10: QA-Checkliste Filter/Performance

## EPIC D – Customer Dashboard Navigation
- D-01: Ziel-Routen + Prefill-Filter festlegen
- D-02: Router-Interface Prefill dokumentieren
- D-03: KPI-Karten klickbar (UiStatCard)
- D-04: Bestellungen-View Prefill open/reorder
- D-05: Lagerbewegungen-View Prefill Datum=heute
- D-06: Tooltip/Hint auf KPI-Karten
- D-07: Accessibility-Check Navigation
- D-08: QA-Checkliste KPI-Navigation

## EPIC E – Customer Orders Verbesserungen
- E-01: Prefill-Logik „Bestellwürdig“ definieren
- E-02: UI-Spezifikation neuer Bestell-Dialog
- E-03: Dialog-Komponente Mehrfachzeilen planen
- E-04: Validierungsregeln festlegen
- E-05: Fehlerdarstellung ohne rote Ränder
- E-06: Prefill „Bestellwürdig“ im Dialog aktivieren
- E-07: Storno-Konzept dokumentieren
- E-08: QA-Checkliste Multi-Add/Validierung
- E-09: Accessibility-Prüfung Dialog
- E-10: Telemetrie/Logging Events definieren

## EPIC F – Offline Queue Fehlerhandling
- F-01: Datenmodell Queue-Einträge dokumentieren
- F-02: Fehlerklassifizierung Mapping
- F-03: UX-Flow Liste + Detail (Tabs/Badges)
- F-04: Komponentenstruktur Queue planen
- F-05: Retry/Löschen gegen Queue-Service verdrahten
- F-06: Auth-spezifischer Login+Sync Flow
- F-07: Fehlertexte/Empty States definieren
- F-08: QA-Checkliste Offline-Queue
- F-09: Telemetrie-Ereignisse (Retry Erfolg/Fehler)
- F-10: Accessibility-Anforderungen Queue

## EPIC G – Dokumentation & Hilfe
- G-01: Doku-Struktur definieren
- G-02: Install/Betrieb Leitfaden skizzieren
- G-03: User-Doku Customer outline
- G-04: User-Doku Admin outline
- G-05: Help-Button Konzept Customer
- G-06: Help/Debug-Bereich Admin
- G-07: Support-Kontaktdaten Config dokumentieren
- G-08: QA-Checkliste Links/Sichtbarkeit

## EPIC H – Monitoring Lightweight
- H-01: Monitoring-Optionen evaluieren
- H-02: Status-API/Endpoint-Konzept
- H-03: Statische Statusseite entwerfen
- H-04: Compose-Snippet ohne Grafana dokumentieren
- H-05: Logs/Health-Check-Prozeduren beschreiben
- H-06: Metrics-Nutzung (Prometheus) erläutern
- H-07: QA/Smoke-Plan Statusseite
- H-08: Security-Notizen Expose/Basisauth

## EPIC I – Kontaktdaten & Support
- I-01: Felddefinitionen/Validierung dokumentieren
- I-02: Backend-Schema/Endpoints globale Kontakte
- I-03: Tenant-Settings Vertriebs-Kontakt planen
- I-04: Admin-UI Formulare globale Kontakte
- I-05: Admin-UI Tenant-Details Kontaktfelder
- I-06: Customer-Frontend Anzeige/Settings konzipieren
- I-07: API-Client/Models Erweiterungen planen
- I-08: QA-Checkliste Validierung/Fallback
- I-09: Datenschutz/Sichtbarkeit dokumentieren
