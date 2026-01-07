# EPIC C – Customer Reporting UX

## 1) Ziel
Berichte & Analysen mit klarer, performanter UX, inkl. Live-Suche, Mehrfachauswahl, Kategorie-Filter, Zeitraumsteuerung und optionalem Export.

## 2) Problem heute
- Reporting-Filter begrenzt, kein konsistenter Mehrfachauswahl-Flow.
- Leere Zustände und Performance-Hinweise fehlen.
- Export-Verhalten uneinheitlich.

## 3) Scope
- Customer-Frontend Reporting-Views und Komponenten.
- Filter UX: Live-Suche nach Artikeln (Prefix), Multi-Select, Kategorie-Filter, Zeitraum, Top-5 Default.
- Export optional (Konzept + UI-Platzhalter).

## 4) Nicht-Ziele
- Keine Backend-Query-Optimierung in diesem Epic.
- Keine neue Chart-Bibliothek; bestehendes Setup nutzen.
- Keine Persistenz von Filter-Presets über Sessions hinaus.

## 5) User Journeys
- User öffnet Berichte, sieht Top-5 Items standardmäßig.
- User tippt Prefix, erhält Vorschläge, wählt mehrere Artikel + Kategorien.
- User setzt Zeitraum (Preset + Custom) und aktualisiert Charts/Tabellen live.
- Optionaler Export: Klick → Download/Modal mit Hinweis auf Umfang.

## 6) UI/UX Regeln
- Filterleiste mit klaren Labels und Tooltips für Performance.
- Chips für aktive Filter, leicht entfernbar.
- Leere Zustände mit Hinweis „Keine Daten im Zeitraum“ und Aktion „Filter zurücksetzen“.
- Ladezustände mit Skeleton/Spinner, keine UI-Sprünge.

## 7) API/Backend Annahmen
- Reporting-Endpunkte unterstützen Query-Parameter `query`, `categories`, `item_ids`, `from`, `to`, `limit`.
- Live-Suche nutzt bestehenden Items-Endpunkt mit Prefix-Filter.
- Export-Endpunkt liefert Datei-Response; optional Stub falls nicht bereit.

## 8) Daten (konzeptionell)
- Filter-State: `{query: string, categories: string[], itemIds: string[], dateRange: {from, to}, limit: number}`.
- Response: KPIs, Serien, Top-Listen; vereinheitlichter Typ für Charts/Tabelle.

### Live-Suche Komponente (C-03)
- Zweck: Artikel-Prefix-Suche für Reporting-Filter, Mehrfachauswahl via Chips.
- Trigger: ab 2 Zeichen, debounce 250–300ms, request-cancel bei neuem Input.
- Datenquelle: bestehender Items-Endpunkt (`GET /inventory/items?query=<prefix>&limit=10`) über zentrale Axios-Instanz und `getTenantHeaders()`.
- UI: Eingabe + Dropdown mit Loader/Empty-State, Option „Alle entfernen“, Chips für ausgewählte Items, Keyboard-Support (Arrow/Enter/Escape).
- Fehler: nutzt `classifyError`; bei Netzwerk/Server Fehler-Hinweis im Dropdown, kein Toast-Spam.
- Caching: Memory-Cache für letzte 10 Queries (prefix-basiert), Treffer 60s halten, um wiederholte Eingaben zu beschleunigen.
- Props/Events (Vue): `modelValue: ItemOption[]`, `placeholder`, `loading` (readonly), `@update:modelValue` (array), `@search` (internal, nicht public).
- Datenformate:
  - `ItemOption`: `{id: string, name: string, sku?: string}`.
  - Response-Mapping: `{id, name, sku}` → `label = sku ? "${sku} – ${name}" : name`.
  - Limit: UI zeigt max 10 Treffer, „Mehr anzeigen“ ist bewusst nicht Teil des Inputs.
- Accessibility:
  - Input `aria-autocomplete="list"`, Dropdown `role="listbox"`, Option `role="option"`.
  - `aria-live="polite"` für „Keine Treffer“.
- Empty/Loading States:
  - Loading: „Suche läuft…“
  - Empty: „Keine Artikel gefunden“
- Error: „Suche derzeit nicht verfügbar“

### Mehrfachauswahl (C-04)
- Ziel: Artikel und Kategorien als Mehrfachauswahl mit Chips, konsistente Interaktion für beide Filter.
- Layout:
  - Eingabefeld + Dropdown (Suchfeld) oben, Chips darunter (wrap).
  - Chips zeigen `label`, optional `sku` als Prefix, `x` zum Entfernen.
- Interaktion:
  - Auswahl per Klick/Enter fügt Chip hinzu und leert Input.
  - „Alle entfernen“ löscht Auswahl (mit Bestätigung bei >5 Chips).
  - Keyboard: Backspace im leeren Input entfernt letzten Chip.
- Limits:
  - Max 25 Artikel, max 10 Kategorien (mit Hinweis „Limit erreicht“).
  - Doppelte Auswahl wird verhindert; bereits gewählte Items im Dropdown disabled.
- States:
  - Loading: Dropdown zeigt Spinner + „Lade Vorschläge…“
  - Empty: „Keine Treffer“, CTA „Filter zurücksetzen“ (optional).
  - Error: „Filter derzeit nicht verfügbar“ (kein Toast-Spam).
- Datenfluss:
  - Article-Chips aus `ItemOption[]`, Kategorie-Chips aus `{id, name}`.
  - Emittiert `update:selectedItems` und `update:selectedCategories`.

### Zeitraum-Presets (C-05)
- Presets:
  - „Letzte 7 Tage“, „Letzte 30 Tage“, „Letzte 90 Tage“.
  - Optional: „Dieses Jahr“ (ab Jan 1) nur wenn Performance ok.
- Custom Range:
  - Date-Picker mit `from`/`to`, Validierung `from <= to`.
  - Max Range 365 Tage, Hinweis bei Überschreitung: „Zeitraum zu groß“.
- Interaktion:
  - Preset-Auswahl setzt `from/to` sofort und triggert Refresh.
  - Wechsel auf Custom hält letzte Preset-Werte als Start.
- Anzeige:
  - Aktiver Preset-Button visuell markiert, Custom zeigt Datumswerte.
## 9) Tasks (umsetzbar, klein)
- **C-01** – Filter-API/Parameter validieren und dokumentieren (Reporting/Items).  
  - Bereich: docs/backend  
  - Dateien/Bereiche: docs/openapi, Epic Abschnitt  
  - Abhängigkeiten: keine  
  - Done: Parameter und Limits festgehalten.
- **C-02** – UX-Flow-Skizze für Reporting-Startseite mit Top-5 Default.  
  - Bereich: docs/ui  
  - Dateien/Bereiche: Wireframe/Markdown  
  - Abhängigkeiten: keine  
  - Done: Flow beschrieben.
- **C-03** – Live-Suche-Komponente (Prefix) entwerfen inkl. Debounce.  
  - Bereich: customer  
  - Dateien/Bereiche: `src/components/reports`  
  - Abhängigkeiten: C-01  
  - Done: Komponentenkonzept + Props/API.
- **C-04** – Mehrfachauswahl für Artikel/Kategorien definieren (Chips + Dropdown).  
  - Bereich: customer  
  - Dateien/Bereiche: Filter-Komponenten  
  - Abhängigkeiten: C-03  
  - Done: UI-Spezifikation fertig.
- **C-05** – Zeitraum-Presets + freies Datum (Calendar oder Inputs) planen.  
  - Bereich: customer  
  - Dateien/Bereiche: Filter-Komponenten  
  - Abhängigkeiten: keine  
  - Done: Presets definiert (7/30/90 Tage, Custom).
- **C-06** – Top-5 Default + freie Auswahl Logik dokumentieren.  
  - Bereich: customer  
  - Dateien/Bereiche: View-Logikbeschreibung  
  - Abhängigkeiten: C-02  
  - Done: Default-Limit + Override beschrieben.
- **C-07** – Leere Zustände/Fehlerzustände Texte definieren.  
  - Bereich: docs/ui  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: keine  
  - Done: Texte und Aktionen hinterlegt.
- **C-08** – Lade- und Performance-Hinweise (Throttling, Max-Limit) dokumentieren.  
  - Bereich: docs  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: C-01  
  - Done: Hinweise fixiert.
- **C-09** – Export-Konzept (Button, Progress, Format) festlegen.  
  - Bereich: customer/docs  
  - Dateien/Bereiche: Epic Abschnitt, UI-Notiz  
  - Abhängigkeiten: C-01  
  - Done: UI/Fehlermeldungen dokumentiert.
- **C-10** – QA-Checkliste (Filter-Kombinationen, Mobile, Darkmode) erstellen.  
  - Bereich: docs  
  - Dateien/Bereiche: QA-Abschnitt  
  - Abhängigkeiten: C-04–C-06  
  - Done: Prüfschritte definiert.

## 10) Akzeptanzkriterien
- Reporting zeigt Top-5 Default und reagiert auf Mehrfachfilter ohne Reload.
- Live-Suche liefert Vorschläge ab 2 Zeichen, debounce aktiv.
- Leere Zustände und Fehlertexte sichtbar mit Reset-Action.
- Export-Option dokumentiert oder umgesetzt (Button sichtbar, Verhalten klar).

## 11) Risiken/Offene Punkte
- Performance bei großen Datenmengen; evtl. Backend-Limits nötig.
- Export-Größe/Timeouts unklar.
- UX-Overload riskant; Filter müssen kompakt bleiben.
