2026-01-06

- Analysierte Views:
  - Customer Frontend: Einstellungen (Formular/Checkbox, Grid-Spalten), Bestellungen (Filter + Tabellenaktionen)
- Erkannte UI-Probleme:
  - Checkbox in Einstellungen ohne konsistente Ausrichtung/Typografie, wirkt ungestylt neben Inputs.
 - Form-Grid-Elemente mit span-2 ohne konsistente Mindestbreite; Inhalte quetschen auf kleineren Breakpoints.
  - Tabellen-Aktionszellen ohne definierte Abstände; Buttons kleben zusammen.
- Umgesetzte Fixes:
  - Neue Utility-Klasse `.checkbox-field` inkl. Checkbox-Sizing/Typografie und Anwendung in Einstellungen-View für Auto-Bestellung.
  - Form-Grid erweitert um `.span-2` Mindestbreite, damit breite Felder stabil bleiben.
  - Utility `.table-actions` ergänzt (Flex mit Gap) für saubere Button-Abstände in Tabellen.

2026-01-06 (Folgeschritt)

- Analysierte Views:
  - Customer Frontend: Kategorien (Formular + Tabelle)
- Erkannte UI-Probleme:
  - Checkbox im Kategorien-Formular nutzt generische Inline-Ausrichtung; Label-Typografie und Checkbox-Größe weichen vom neuen Pattern ab.
  - Tabellen-Aktionszellen in Kategorien sollen die neue `.table-actions` Utility nutzen (bereits Klassen vorhanden, Utility greift nun global).
- Umgesetzte Fixes:
  - Kategorien-Formular auf `.checkbox-field` mit einheitlichem Label-Style umgestellt.

2026-01-06 (Folgeschritt 2)

- Analysierte Views:
  - Customer Frontend: Artikelverwaltung (Stammdaten + Create-Form)
- Erkannte UI-Probleme:
  - Checkboxen für Artikelstatus (bearbeiten/anlegen) nutzen lokale Styles; Abstände/Typografie weichen vom neuen Pattern ab.
- Umgesetzte Fixes:
  - Beide Artikelstatus-Checkboxen auf `.checkbox-field` umgestellt, inkl. einheitlicher Label-Typo und aria-labels; lokale `.checkbox`-Styles entfernt.

2026-01-06 (Folgeschritt 3)

- Analysierte Views:
  - Customer Frontend: Bestellungen (Filterbereich + Tabellenaktionen)
- Erkannte UI-Probleme:
  - Filter (Status + Suche) liegen ungruppiert in einer breiten Grid-Reihe; auf mittleren Breakpoints gequetscht und ohne erklärende Hint.
- Umgesetzte Fixes:
  - Filter in eine kompakte `.filter-card two-column` überführt, mit klaren Labels und Hint für Suchverhalten; nutzt bestehende Utilities und reduziert Quetschung auf mittleren Breakpoints.

2026-01-06 (Folgeschritt 4)

- Analysierte Views:
  - Customer Frontend: Bestellungen (Tabellen-Aktionsspalten)
- Erkannte UI-Probleme:
  - Aktionsspalten nicht eindeutig rechts ausgerichtet, Buttons wirken uneinheitlich platziert.
- Umgesetzte Fixes:
  - Aktionen-Spalten in allen Bestellungen-Tabellen rechts ausgerichtet (`text-right` + `.table-actions`), damit Buttons konsistent gebündelt sind.
