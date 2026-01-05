# COMPONENT CONVENTIONS – UI-Bausteine

## Ziel
Views enthalten nur Struktur und Datenlogik. Styling kommt aus zentralen UI-Bausteinen, Utilities und Tokens je App.

## Ordnerstruktur je App
- `src/components/ui/`
  - `UiPage.vue`: Seiten-Wrapper (max-width, Padding, Hintergrund).
  - `UiSection.vue`: Abschnitt mit Titel, optionalen Actions, Trenner/Spacing.
  - `UiCard.vue`: Standard-Card mit Header/Body-Slots, Radius/Shadow aus Tokens.
  - `UiStatCard.vue`: KPI-Card mit Eyebrow/Value/Hint, nutzt Status/Primary-Tokens.
  - `UiToolbar.vue`: Actions/Filter-Leiste mit responsivem Wrapping.
  - `UiEmptyState.vue`: Leerer Zustand (Icon/Title/Hint/Action).
  - Optional `UiToastHost.vue`, falls Toast-Markup vereinheitlicht werden muss.

## Styling-Regeln
- Keine Inline-Styles, keine hart gecodeten Farben/Pixel. Alles über Tokens (`tokens.css`) und Utilities (`utilities.css`).
- Keine `<style scoped>` für Farben/Spacing; falls Scoped nötig, nur für strukturelle Ausrichtung (keine Token-Bypässe).
- Typografie und Spacing folgen der Skala aus `THEME_TOKENS.md`.

## PrimeVue-Integration
- Customer-Frontend: PrimeVue-Komponenten dürfen in UI-Bausteinen genutzt werden, das Styling erfolgt über Tokens/`theme.css`.
- Admin-Frontend: Bleibt bei nativen HTML-Elementen; gemeinsame Klassen (Buttons, Tags, Tables) werden in `utilities.css` oder UI-Bausteinen gekapselt.

## Responsive
- Toolbars/Filter müssen auf schmale Breiten umbrechen (`flex-wrap`, `gap` aus Tokens).
- Tabellen erhalten `overflow-x` oder werden in mobile Card-Listen verwandelt; Entscheidung pro App/View dokumentieren.

## Barrierefreiheit
- Buttons/Links mit `aria-label` bei Icon-Only-Actions.
- Toast/Status-Komponenten mit `role="status"`/`aria-live="polite"`.
- Focus-Ringe nutzen den gemeinsamen `--focus-ring` Token.
