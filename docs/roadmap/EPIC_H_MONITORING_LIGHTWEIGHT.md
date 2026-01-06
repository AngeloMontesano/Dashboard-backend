# EPIC H – Monitoring Lightweight

## 1) Ziel
Leichtgewichtiges DB/Service-Monitoring ohne Grafana: Statusseiten, Logs, Healthchecks bereitstellen.

## 2) Problem heute
- Kein kompaktes Monitoring ohne Grafana vorhanden.
- Health/DB-Status nur per Einzel-Endpoints, keine Übersicht.

## 3) Scope
- Optionen für Monitoring (Docker-gestützt) dokumentieren.
- Einfache Statusseiten/Healthchecks und Log-Zugriff definieren.

## 4) Nicht-Ziele
- Kein Vollausbau (Alerting/Tracing) in diesem Epic.
- Keine Grafana/Prometheus-Fullstack-Erweiterung.

## 5) User Journeys
- Operator öffnet leichte Statusseite und sieht API/DB-Status, Version, letzte Checks.
- Operator prüft Logs über einfaches UI oder CLI-Anleitung.
- Operator ruft Health/DB/metrics Endpunkte manuell/automatisiert ab.

## 6) UI/UX Regeln
- Statusseite klar, ohne Login wenn intern; zeigt Health/DB/Version.
- Farbcodes für ok/degraded/down, Link zu Logs/Docs.

## 7) API/Backend Annahmen
- Bestehende Endpunkte: `/health`, `/health/db`, `/meta`, `/metrics` (Prometheus) bleiben.
- Optionaler neuer Lightweight-UI-Endpunkt, der diese sammelt.

## 8) Daten (konzeptionell)
- Statusobjekt: `{api: ok|degraded|down, db: ok|down, version, commit, timestamp}`.
- Logquellen: Container-Logs (`docker logs`), evtl. Tail-Endpoint.

## 9) Tasks (umsetzbar, klein)
- **H-01** – Monitoring-Optionen evaluieren (caddy-status, static HTML, simple dashboard).  
  - Bereich: docs/devops  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: keine  
  - Done: Optionen + Pros/Cons gelistet.
- **H-02** – Status-API/Endpoint-Konzept erstellen (Aggregation von /health,/meta).  
  - Bereich: backend/docs  
  - Dateien/Bereiche: Konzeptabschnitt  
  - Abhängigkeiten: keine  
  - Done: Endpoint-Schema skizziert.
- **H-03** – Statische Statusseite entwerfen (HTML/JS minimal).  
  - Bereich: docs  
  - Dateien/Bereiche: Mockup/Plan  
  - Abhängigkeiten: H-02  
  - Done: Layout + Felder definiert.
- **H-04** – Deploy-Variante ohne Grafana dokumentieren (Docker Compose Snippet).  
  - Bereich: devops/docs  
  - Dateien/Bereiche: README Abschnitt  
  - Abhängigkeiten: H-01  
  - Done: Snippet veröffentlicht.
- **H-05** – Logs/Health-Check-Prozeduren beschreiben (Befehle, Schwellen).  
  - Bereich: docs  
  - Dateien/Bereiche: Betriebskapitel  
  - Abhängigkeiten: H-04  
  - Done: Schritte festgehalten.
- **H-06** – Metrics-Nutzung kurz erläutern (Prometheus Scrape).  
  - Bereich: docs  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: H-02  
  - Done: Scrape-URL/Labels dokumentiert.
- **H-07** – QA/Smoke-Plan für Statusseite (Up/Down-Simulation) erstellen.  
  - Bereich: docs  
  - Dateien/Bereiche: QA-Abschnitt  
  - Abhängigkeiten: H-03  
  - Done: Testschritte notiert.
- **H-08** – Security-Notizen (Expose nur intern/Basisauth) ergänzen.  
  - Bereich: devops/docs  
  - Dateien/Bereiche: Konzeptabschnitt  
  - Abhängigkeiten: H-02  
  - Done: Hinweise vorhanden.

## 10) Akzeptanzkriterien
- Dokumentierte Option für leichtes Monitoring ohne Grafana.
- Statusseite/Endpoint-Konzept zeigt API/DB/Version kompakt.
- Betrieb/Logs/Health-Prozeduren beschrieben.

## 11) Risiken/Offene Punkte
- Sicherheit bei öffentlichem Expose der Statusseite.
- Synchronität der Statusdaten ohne Cache.
- Metrics können je nach Hosting nicht erreichbar sein.
