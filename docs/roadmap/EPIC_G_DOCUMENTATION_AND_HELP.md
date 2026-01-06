# EPIC G – Dokumentation & Hilfe

## 1) Ziel
Technische Doku für Betrieb/Installation und verständliche User-Doku (Customer/Admin) bereitstellen; Help-Buttons mit Support/Debug-Konzept.

## 2) Problem heute
- Doku-Fragmente verteilt, keine klare Struktur.
- Kein Help/Support-Einstieg in den Frontends.
- Debug/Support-Infos für Admins fehlen.

## 3) Scope
- Struktur für technische Doku (Install, Betrieb, Monitoring-Light Anbindung).
- User-Doku Customer/Admin (Grundflows, FAQ).
- Help-Button-Konzepte: Customer Hilfe + Support, Admin Debug-Bereich.

## 4) Nicht-Ziele
- Keine neue Support-Backend-Funktionalität.
- Keine Chat/Live-Support-Integration.

## 5) User Journeys
- Admin liest Install-/Betriebsanleitung vor Deployment.
- Customer klickt „Hilfe“ im UI und landet auf Hilfeseite/Modal mit FAQ + Support-Link.
- Admin öffnet Debug-Bereich (Systemstatus, Logs-Hinweise) über Help/Support.

## 6) UI/UX Regeln
- Help-Button klar sichtbar (Topbar/Settings), keine Modal-Überladung.
- Links zu Doku/Support im neuen Tab, deutliche Beschriftung.
- Debug-Bereich nur im Admin, mit Warnhinweis für sensible Daten.

## 7) API/Backend Annahmen
- Keine neuen Endpunkte nötig; Help/Support-Links statisch konfiguriert.

## 8) Daten (konzeptionell)
- Doku-Struktur: `/docs/` Ordner mit Unterkapiteln (Install, Betrieb, Troubleshooting, FAQ Customer/Admin).
- Help-Konfiguration: statische Links/Emails in Config/Env.

## 9) Tasks (umsetzbar, klein)
- **G-01** – Doku-Struktur definieren (Kapitel, Ordner).  
  - Bereich: docs  
  - Dateien/Bereiche: README/Index für Doku  
  - Abhängigkeiten: keine  
  - Done: Strukturplan veröffentlicht.
- **G-02** – Technische Install/Betrieb-Anleitung skizzieren (Docker, Env, Health).  
  - Bereich: docs/backend  
  - Dateien/Bereiche: neuer Leitfaden  
  - Abhängigkeiten: G-01  
  - Done: Kapitelentwurf vorhanden.
- **G-03** – User-Doku Customer (Login, Dashboard, Bestellungen, Reporting) outline.  
  - Bereich: docs/customer  
  - Dateien/Bereiche: Markdown Outlines  
  - Abhängigkeiten: G-01  
  - Done: Kapitel + Screens gelistet.
- **G-04** – User-Doku Admin (Tenants, Benutzer, globale Kataloge) outline.  
  - Bereich: docs/admin  
  - Dateien/Bereiche: Markdown Outline  
  - Abhängigkeiten: G-01  
  - Done: Kapitel gelistet.
- **G-05** – Help-Button Konzept Customer (Position, Inhalte, Support-Link) festlegen.  
  - Bereich: customer  
  - Dateien/Bereiche: Epic Abschnitt, ggf. UI-Konzept  
  - Abhängigkeiten: G-03  
  - Done: Konzept dokumentiert.
- **G-06** – Help/Debug-Bereich Admin planen (Systemstatus, Logs-Hinweise).  
  - Bereich: admin  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: G-02  
  - Done: Inhalte definiert.
- **G-07** – Support-Kontaktdatenablage (Config/Env) dokumentieren.  
  - Bereich: docs/backend  
  - Dateien/Bereiche: Konfig-Abschnitt  
  - Abhängigkeiten: keine  
  - Done: Felder/Beispiele notiert.
- **G-08** – QA-Checkliste (Links, Rollen, Sichtbarkeit) erstellen.  
  - Bereich: docs  
  - Dateien/Bereiche: QA-Abschnitt  
  - Abhängigkeiten: G-05, G-06  
  - Done: Liste vorhanden.

## 10) Akzeptanzkriterien
- Doku-Index beschreibt technische und User-Doku-Struktur.
- Help-Buttons sind konzeptionell verortet (Customer + Admin).
- Support/Debug-Informationen dokumentiert, keine toten Links.

## 11) Risiken/Offene Punkte
- Pflegeaufwand für Doku hoch; Ownership klären.
- Support-Kontakte können sich ändern; Config-Quelle definieren.
