# CSS and UI Conventions

## Grundsätze
- Keine Redesigns in diesem Schritt; nur Konsistenzregeln dokumentieren.
- Bestehende Design-Systeme bleiben: PrimeVue im Customer-Frontend, bestehende Admin-Stile im Admin-Frontend.
- Wiederverwendbare Klassen und Tokens bevorzugen statt ad-hoc Inline-Styling.

## Tokens und Basisklassen
- Farben, Abstände und Typografie kommen aus den vorhandenen globalen Styles (`styles`-Ordner je Frontend).
- Buttons nutzen konsistente Primär-/Sekundär-Klassen statt lokaler Varianten.
- Karten/Panels verwenden gemeinsame Layout-Klassen (Padding, Border, Shadow), keine duplizierten Inline-Box-Shadows.

## PrimeVue (Customer)
- Beibehaltener Einsatz von PrimeVue-Komponenten; Custom-Styles nur über Token/Utility-Klassen ergänzen.
- Keine Überschreibung der PrimeVue-Basisfarben pro View; Anpassungen über zentrale Theme-Variablen vornehmen.

## Admin-Design
- Bestehendes Admin-Theme bleibt unverändert; neue Elemente sollen bestehende Utility-Klassen (z. B. `.panel`, `.muted`, `.mono`, `.row`, `.col`) nutzen.
- Fokus auf konsistente Spacing- und Typografie-Regeln, keine neuen Farbschemata.

## Kandidaten zur Zentralisierung
- Buttons (Primär/Sekundär/Destruktiv) über gemeinsame Klassen kapseln.
- Cards/Panels mit einheitlichen Header-/Body-Abständen.
- Page-Layouts (Sidebar + Content) mit wiederverwendbaren Flex/Grid-Helfern.

## Do/Don’t
- ✅ Do: Utility-Klassen wiederverwenden, Tokens nutzen, Komponenten theming-fähig halten.
- ❌ Don’t: Neue Inline-Styles, duplizierte Button-Varianten, globale User-Konzepte im Customer-Kontext einführen.
