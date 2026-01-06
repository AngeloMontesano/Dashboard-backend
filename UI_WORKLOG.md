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
