# Migration Legacy-Modul `/old_lm`

## Scope
- Fachliche Funktionen aus dem Legacy-Flask-Code (`/old_lm/*.py`) in das neue Multi-Tenant-System überführen (Backend + Customer-Frontend).
- Keine Redesigns, nur Funktionsparität: Artikel/Bestand, Lagerbewegungen, Inventur, Berichte/Verbrauch, Bestellungen, Einstellungen/Exporte.
- Admin- und Customer-Apps bleiben getrennt; alle Frontend-Calls ausschließlich über `/api`.

## Reihenfolge (Phasen)
1. Reverse Engineering Legacy-Code (Funktionen, Felder, Regeln, Exporte) ✅
2. Soll-Ist-Abgleich mit aktuellem Backend/Frontend/OpenAPI (Gap-Liste) ✅
3. Task-Liste anlegen (`docs/roadmap/TASKS_MIGRATION_OLD_LM.md`) ✅
4. Backend-Lücken schließen (Endpunkte/Business-Logik gemäß Legacy, Tenant-sicher)
5. Customer-Frontend mit echten Daten verdrahten (Views, API-Wrapper, OpenAPI-Typen)
6. QA: Proxy-/Axios-Regeln, Builds (Backend/Customer/Admin), keine festen Hosts, keine Dummy-Daten

## Definition of Done
- Alle Legacy-Funktionen sind im neuen Backend als Endpunkte/Services verfügbar (Tenant-scoped) und über OpenAPI beschrieben.
- Customer-Frontend-Views liefern echte Daten (keine Dummy-KPIs); Exporte funktionieren (CSV/XLSX/PDF gemäß Legacy-Schema, falls vorhanden).
- Bestandsänderungen sind idempotent, führen kein Negativ-Bestand herbei und werden als Bewegungen protokolliert.
- Einstellungen (Firmendaten, Auto-Bestellung/Schwellen, Empfänger/Exports, Mass Import/Export) sind über `/api` bedienbar.
- Dokumentation aktualisiert: Roadmap, Tasks, WORKLOG, TODO.

## Decisions
- Legacy-Felder wie `pf_artikel_id`, `ean`, `mindestbestand`, `sollbestand` werden übernommen/migriert; Mapping zu bestehendem Item-Modell (SKU/Barcode) ist herzustellen, kein Stillstand durch reine SKU-Nutzung.
- Barcode-Flows bleiben API-basiert (kein direktes DB-Schreiben); Bewegungen protokollieren Menge, Typ (IN/OUT), Zeitstempel, optional Notiz.
- Reporting nutzt serverseitige Aggregation; Client-seitige Fallbacks aus Bewegungen nur als Übergang.
- Exporte folgen Legacy-Spaltenreihenfolge; neue Felder dürfen ergänzt werden, solange Legacy-Felder erhalten bleiben.

## Known Issues
- DB-Backfill/Migration für neue Settings-Felder (Ansprechpartner, PLZ/Ort, Filialnummer, Steuernummer) noch ausstehend.
- Frontend-Feinschliff (Tokens/Responsive) für Customer-Ansichten Inventur/Bestellungen/Berichte offen.
- Legacy-Flash-API bleibt ungemappt (Frontend nutzt lokale Toasts).

---

## Funktionsmatrix (Phase 1 – Legacy `/old_lm`)

### Artikel (`old_lm/artikel.py`)
- Flows: HTML-Übersicht, API-CRUD (`/api/artikel/` GET/POST, `/api/artikel/<id>` PUT/DELETE), Massen-Speichern über `save_all` (Form-Felder pro `pf_artikel_id`).
- Daten: `pf_artikel_id`, `name`, `ean`, `kategorie`, `bestand`, `mindestbestand`, `sollbestand` (implizit via Bestellungen/Dashboard), `lagerort`, `preis`.
- Regeln: `save_all` schreibt nur geänderte Felder je `pf_artikel_id`; fehlende Artikel werden geloggt.

### Lagerbewegungen (`old_lm/bestandsverwaltung.py`)
- Flows: HTML-Übersicht letzter Bewegungen; API `/entnahme` und `/zugang` (POST JSON mit `barcode`).
- Daten/Regeln: Barcode sucht Artikel (`ean`); Entnahme dekrementiert Bestand, aber nie < 0 (`max(bestand-1,0)`); Zugang inkrementiert. Bewegungen werden als Datensätze mit `typ` (`Entnahme`/`Zugang`), `menge=1`, `artikel_id` gespeichert.

### Inventur (`old_lm/inventur.py`)
- Flows: Tabelle aller Artikel, Export als Excel (`inventur.xlsx`), Save-All (`save_all` JSON `updates[]` mit `id` = `pf_artikel_id`, `bestand`).
- Export-Spalten: `Artikel-ID`, `Name`, `Barcode`, `Kategorie`, `Soll`, `Min`, `Bestand` (Werte: `pf_artikel_id`, `name`, `ean`, `kategorie`, `bestand`, `sollbestand`, `mindestbestand`).

### Berichte/Verbrauch (`old_lm/berichte.py`)
- Flows: Verbrauchs-Dashboard, Daten-API `/daten` (Monatliche SUM(Entnahme) je Artikel), Exporte: CSV, Excel, PDF.
- Regeln: Aggregation aus `lagerbewegung` (nur `typ='Entnahme'`); Gruppierung `DATE_FORMAT(zeit,'%Y-%m')`, Artikel-Name.
- Exporte: CSV/Excel mit Spalten `Artikel`, `Monat`, `Verbrauch`; PDF mit Bar- und Liniendiagramm, filterbar via `artikel` (Liste), `start`, `end` (YYYY-MM), optional Artikel-Filter.

### Bestellungen (`old_lm/bestellungen.py`)
- Flows: Übersicht „bestellwürdig“ (Artikel unter `sollbestand`), offene/erledigte Bestellungen gruppiert nach `bestellnummer`; Artikel-Auswahl per Dropdown (`select_artikel`), PDF-Erzeugung (`/pdf` POST), Status-Änderungen (`/stornieren`, `/erledigt`), CC-E-Mail-Versand optional.
- Regeln: Bestellnummer `ORDER-<uuid8>`; erledigte Bestellungen erhöhen Artikel-Bestand um Positionsmenge; `check_bestellt` liefert offene Mengen + Bestellnummern pro Artikel.
- Daten: `Bestellung` (status Offen/Erledigt/Storniert, `bestelldatum`), `Bestellposition` (Artikel `pf_artikel_id`, `menge`), Kunde/Administratives für E-Mail.
- Export: PDF mit Artikel-Liste (ID, Name, Bestand, Sollbestand, Bestellmenge) pro Bestellung.

### Einstellungen (`old_lm/einstellungen.py`)
- Flows: Firmendaten speichern (`Kunde`), Auto-Bestellung + Minimum, Empfänger + Export-Format, Test-E-Mail; Mass-Export/Import.
- Daten/Regeln: `Administratives` key-value (`auto_bestellung`, `auto_bestellung_min`, `bestell_email_empfaenger`, `export_format`); Test-E-Mail liest `scripts/smtp.json`.
- Mass Export: Excel aller Artikel mit Spalten `Artikel-ID`, `Name`, `Barcode`, `Kategorie`, `Soll`, `Min`, `Bestand`, `Haltbarkeit`, `Charge`, `Kunden-ID`, `Lagerort`, `Preis`, `Beschreibung`, `Letzte Änderung`, `Letzte Bestellung`, `Bestellt`.
- Mass Import: XLSX (`Artikel-ID`, `Name`, `Barcode`, `Kategorie`, `Soll`, `Min`, `Bestand`, `Haltbarkeit`, `Charge`, `Kunden-ID`, `Lagerort`, `Preis`, `Beschreibung`, ...); aktualisiert oder legt Artikel an, setzt `letzte_bestellung` falls leer.

### Flash (`old_lm/flash.py`)
- Flow: `/get_flash_messages` liefert aktuelle Flash-Messages als JSON (`category`, `text`).

---

## Gap-Liste Soll-Ist (Phase 2)
- **Artikel/Inventar:** Neues Backend hat nur `items`/`categories` (SKU/Barcode, `quantity`, `min_stock`, `target_stock`, `order_mode`), keine `pf_artikel_id`, `sollbestand`, `mindestbestand`, `lagerort`, `haltbarkeit`, `preis`. Bulk-Update (`save_all`) und HTML-Übersicht fehlen. Frontend-Artikel-View nutzt Items-API, aber Legacy-Felder/Exporte fehlen.
- **Lagerbewegungen:** POST `/inventory/movements` existiert (IN/OUT mit `client_tx_id`, qty, note) und verhindert negativen Bestand; GET-Liste/Filter für Reporting war fehlend – jetzt ergänzt (T1), Reporting-/Export-Endpunkte stehen weiter aus. Legacy verlangt Barcode-IN/OUT (Menge 1) und speichert Typ „Entnahme/Zugang“.
- **Inventur:** Bulk-Update + Excel-Export mit Legacy-Spalten ergänzt (T2 erfüllt); Frontend-Inventur zeigt weiterhin Platzhalter-KPIs ohne API-Anbindung.
- **Berichte/Verbrauch:** Backend-Endpunkte `/inventory/report` + Exporte ergänzt (CSV/Excel) auf Basis der Bewegungsaggregation; Frontend nutzt noch den Fallback und muss angebunden werden.
- **Bestellungen:** Bestellwürdig-Liste (`/inventory/orders/recommended`) und Bestellungen mit Statuswechsel sind verfügbar (`/inventory/orders`, `/inventory/orders/{id}`, `/inventory/orders/{id}/complete|cancel`), Abschluss erhöht den Bestand und erzeugt Bewegungen. E-Mail-Versand vorhanden (`/inventory/orders/{id}/email`), PDF-Export verfügbar (`/inventory/orders/{id}/pdf`). Filter/Suche/Canceled-Übersicht im Customer-Frontend ergänzt.
- **Einstellungen/Firmendaten:** Basis-Settings je Tenant sind verfügbar (`/inventory/settings` GET/PUT: Firmendaten, Auto-Bestellung an/aus + Schwelle, Empfänger, Export-Format, Adresse/Telefon) plus Legacy-Admin-Metadaten (Ansprechpartner, PLZ/Ort, Filialnummer, Steuernummer). Mass-Export/Import via Excel hinzugefügt (`/inventory/settings/export`, `/inventory/settings/import`). Test-E-Mail verfügbar (`/inventory/settings/test-email`) mit SMTP-Config. Hinweis: DB-Backfill für neue Settings-Felder einplanen.
- **Flash/Status:** Keine Entsprechung für Flash-API; Frontend setzt Toasts lokal.
