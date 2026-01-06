# EPIC B – Globale Kataloge & Branchen

## 1) Ziel
Globale Artikel/Kategorien/Typen/Branchen zentral im Admin pflegen und Tenants mit Branchenfeldern ausstatten.

## 2) Problem heute
- Keine globalen Kataloge; jede Tenant-Datenbasis separat.
- Branchenzuordnung zu Artikeln fehlt; Tenant kennt keine Branche.
- Admin-UI hat keine Flows für globale Katalogpflege.

## 3) Scope
- Admin: Globale Artikel/Kategorien/Typen/Branchen anlegen/bearbeiten.
- Mapping Branche → globale Artikel.
- Tenant-Detail: Branche als Pflichtfeld (Firma & Adresse).
- Verteilungskonzept dokumentieren, keine Auslieferung an Tenants im Code.

## 4) Nicht-Ziele
- Keine automatische Migration bestehender Tenant-Daten.
- Keine Synchronisation in Customer-Frontend in diesem Epic.
- Keine Preis-/Lagerlogikänderungen.

## 5) User Journeys
- Admin öffnet „Globale Kataloge“ und legt Branchen + Kategorien + Typen an.
- Admin weist globalen Artikeln Branchen zu und markiert aktiv.
- Admin bearbeitet Tenant-Stammdaten und setzt Branche (Dropdown) in Firmen- und Adressbereich.

## 6) UI/UX Regeln
- Listen mit Filter (Branche, Status), Inline-Badges „Global“.
- Formulare mit Pflichtfeld-Markierung für Branche, Dropdowns mit Suche.
- Warnungen bei Löschungen, wenn Mapping besteht.

## 7) API/Backend Annahmen
- Neue Admin-Endpunkte `/admin/global/categories|types|industries|items` mit CRUD (siehe `docs/openapi/GLOBAL_CATALOG.md`).
- Tenant-Entity erweitert um `industry_id` (optional Pflicht in UI).
- Mapping-Tabelle Branche → globale Artikel.
- Listen liefern Paging-Metadaten `{total, limit, offset}` (Default `limit=50`, max 200), Headerpflicht `X-Admin-Key` (optional `X-Admin-Actor`); Fehlercodes umfassen Referenz-Konflikte (`industry_in_use/category_in_use/item_in_use`) und System-Schutz (`forbidden_system_record`).

## 8) Daten (konzeptionell)
- Tabellen:
  - `industries` (id UUID PK, name uniq, is_active bool, timestamps).
  - `global_categories` (id UUID PK, name uniq, is_active, is_system bool).
  - `global_types` (id UUID PK, name uniq, is_active).
  - `global_items` (id UUID PK, sku uniq, name, description, type_id FK, category_id FK, industry_id FK nullable, is_active).
  - Mapping `industry_global_items` (industry_id FK, item_id FK, PK (industry_id, item_id)).
- Tenant-Felder: `industry_id` in Firma + Adresse (FK auf `industries`).
- Index-Regeln: unique auf Namen (lowercase) für Kategorien/Typen/Branchen, unique SKU auf globalen Artikeln, FK-Constraints `ON DELETE RESTRICT`.
- Details in `docs/openapi/GLOBAL_CATALOG.md`.

## 9) Tasks (umsetzbar, klein)
- **B-01** – Datenmodell-Entwurf dokumentieren (Tabellen, Relationen, Constraints).  
  - Bereich: docs/backend  
  - Dateien/Bereiche: docs/openapi, Architektur-Notiz  
  - Abhängigkeiten: keine  
  - Done: Modellskizze mit Keys/Indexes.
- **B-02** – Admin-API-Spezifikationen für globale Kategorien/Typen/Branchen definieren.  
  - Bereich: docs/backend  
  - Dateien/Bereiche: docs/openapi  
  - Abhängigkeiten: B-01  
  - Done: Endpunkte + Schemas dokumentiert.
- **B-03** – Alembic-Entwurf für neue globalen Tabellen und Tenant-Feld.  
  - Bereich: backend  
  - Dateien/Bereiche: alembic/versions Draft  
  - Abhängigkeiten: B-01  
  - Done: Migration-Skript vorbereitet, noch nicht ausgeführt.
- **B-04** – Admin-UI: Navigationspunkt „Globale Kataloge“ anlegen.  
  - Bereich: admin  
  - Dateien/Bereiche: `src/App.vue` Navigation, neue View-Shell  
  - Abhängigkeiten: B-02  
  - Done: Menüpunkt vorhanden, zeigt Platzhalter.
- **B-05** – View „Globale Kategorien/Typen“ mit Listen + Create-Form.  
  - Bereich: admin  
  - Dateien/Bereiche: neue Views/Components  
  - Abhängigkeiten: B-04  
  - Done: CRUD-UI mit Status-Badges.
- **B-06** – View „Globale Artikel“ inkl. Branche/Typ-Auswahl.  
  - Bereich: admin  
  - Dateien/Bereiche: neue Components  
  - Abhängigkeiten: B-05  
  - Done: Liste + Create/Edit-Dialog mit Dropdowns.
- **B-07** – Branche-Mapping zu globalen Artikeln (Filter + Bulk-Zuordnung).  
  - Bereich: admin  
  - Dateien/Bereiche: globale Artikel-View  
  - Abhängigkeiten: B-06  
  - Done: Artikel nach Branche filterbar, Zuordnung speicherbar.
- **B-08** – Tenant-Detail: Branche als Dropdown in Firmen- und Adressblock.  
  - Bereich: admin  
  - Dateien/Bereiche: `AdminTenantsView`, Forms  
  - Abhängigkeiten: B-02  
  - Done: Feld validiert, wird gespeichert.
- **B-09** – API-Wiring Admin-Client für neue globalen Endpunkte.  
  - Bereich: admin/backend  
  - Dateien/Bereiche: `src/api/admin.ts`, Backend-Router  
  - Abhängigkeiten: B-02, B-03  
  - Done: CRUD-Aufrufe funktionieren in Dev.
- **B-10** – Konzept zur Verteilung an Tenants dokumentieren (kein Code).  
  - Bereich: docs  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: B-01  
  - Done: Mechanismus (Sync/Cache) beschrieben.
- **B-11** – Akzeptanz-Tests definieren (UI-Flow + API-Checks).  
  - Bereich: docs  
  - Dateien/Bereiche: QA-Checkliste  
  - Abhängigkeiten: B-05–B-09  
  - Done: Liste mit Prüfschritten.

## 10) Akzeptanzkriterien
- Admin kann Branchen, Kategorien, Typen, globale Artikel CRUD ausführen.
- Branche ist in Tenant-Firmendaten Pflichtfeld (validiert) und wird gespeichert.
- Filter nach Branche funktionieren in globalen Artikeln.
- Admin-Global-Endpunkte erzwingen `X-Admin-Key` und liefern nackte Ressourcen/Listen mit `{total, limit, offset}` ohne zusätzliches `data`-Wrapping.
- API-Listen enthalten Paging-Metadaten, eindeutige Fehlercodes spiegeln Referenz- und System-Schutzfälle wider.
- Datenmodell für spätere Tenant-Sync dokumentiert.

## 11) Risiken/Offene Punkte
- Datenmigration bestehender Tenants ungeklärt.
- Performance bei vielen globalen Artikeln (Paging nötig).
- Konflikte zwischen globalen und tenant-spezifischen Kategorien müssen klar geregelt werden.
