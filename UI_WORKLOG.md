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
