# DESIGN SYSTEM – Frontends Admin & Customer

## Ziele
- Beide Frontends wirken wie eine gemeinsame Plattform, bleiben aber separate Apps (keine Shared-Pakete).
- Light Mode orientiert sich am bisherigen Customer-Look (hell, ruhiges Grau auf Weiß, leichte Transparenzen).
- Dark Mode orientiert sich am bisherigen Admin-Look (dunkle Flächen, klare Sektionen, transparente Cards, großzügige Abstände).
- PrimeVue bleibt im Customer-Frontend; Admin behält sein Custom-CSS, erhält aber dieselben Tokens/Abstände.
- Keine Styling-Details in Views: Farben/Spacing/Typografie kommen aus Tokens, Utilities oder UI-Bausteinen.

## Baseline je App (Ist-Zustand)
- **Admin (`admin_frontend/admin-ui`)**
  - Globale Styles werden in `src/main.ts` geladen: `styles/tokens.css`, `styles/base.css`, `styles/layout.css`.
  - Eigenes Designsystem ohne PrimeVue; Buttons/Cards/Table-Styles sind in `layout.css` definiert.
  - Theme-Auswahl per Klasse (`theme-dark`, `theme-ocean`, `theme-classic`) wird in `App.vue` gesetzt und in `sessionStorage` gehalten.
- **Customer (`customer_frontend/customer-ui`)**
  - Globale Styles aus `src/styles/tokens.css` und `src/styles/layout.css`, geladen in `src/main.ts`.
  - PrimeVue ist aktiv (Lara Preset) inkl. ToastService; zusätzliche eigene Cards/Buttons/Layouts in `layout.css`.
  - Theme-State via `useTheme` (SessionStorage), Klasse wird am App-Root gesetzt; kein System-Default.

## Zielarchitektur je App
- Styles pro App unter `src/styles/`:
  - `tokens.css`: Farb-/Spacing-/Radius-/Shadow-Tokens für Light/Dark.
  - `theme.css`: Mapping Tokens -> Oberflächen + PrimeVue-Overrides (nur pro App, kein Sharing).
  - `utilities.css`: Layout-Utilities (`.page`, `.section`, `.card-grid`, `.stack`, `.toolbar`, `.muted`, `.divider`).
  - `index.css` (oder `main.css`): importiert Tokens + Theme + Utilities.
- UI-Bausteine pro App unter `src/components/ui/`:
  - `UiPage`, `UiSection`, `UiCard`, `UiStatCard`, `UiToolbar`, `UiEmptyState` (plus optional `UiToastHost`).
  - Nutzen ausschließlich Tokens/Utilities; keine Inline-Styles, keine Scoped-Styles für Farben/Abstände.
- Theme-Steuerung:
  - `useTheme.ts` pro App, steuert `data-theme="light|dark|system"` auf `document.documentElement`, default folgt System.
  - Persistenz via `localStorage`; Toggle in bestehender Topbar/Sidebar.
- Mobile First:
  - Breakpoints früh ansetzen (`max-width: 1100px` o.ä.), Grids/Toolbars müssen stacken, Tabellen brauchen `overflow-x` oder Card-Listen-Alternativen.

## Komponenten- und Layout-Leitplanken
- Page-Layout: `UiPage` kapselt Max-Width, Padding, Hintergrund; `UiSection` trennt Abschnitte mit Header (Titel + Actions).
- Cards: `UiCard`/`UiStatCard` übernehmen Radius/Shadow/Spacing; keine Card-spezifischen Styles in Views.
- Toolbars/Filter: `UiToolbar` stellt Gap/Wrapping sicher, Buttons stammen aus zentralen Klassen/PrimeVue-Buttons.
- Empty States: `UiEmptyState` als Standard für leere Tabellen/Listen, nutzt Tokens (Text-muted, Border, Surface).
- Toasts/Overlays: zentral gestylt (leicht transparent, ruhiger Stil), keine per-View-Overrides.

## Verbotene Muster
- Inline-Styles oder hart gecodete Farben/Pixelwerte in Templates/Views.
- Neue `<style scoped>`-Blöcke für Farben/Abstände/Typografie in Views (nur strukturelle Ausnahmen).
- Ad-hoc PrimeVue-Overrides in einzelnen Views; alle Anpassungen laufen über `theme.css`.

## Übergangsschritte
- Task 1: Ist-Aufnahme (dieses Dokument).
- Task 2–4: Tokens, Utilities, UI-Bausteine anlegen und schrittweise in Pilot-Views anwenden.
- Task 5–7: Dark-Mode-System, PrimeVue-Overlays/Toasts zentralisieren, Responsive-Regeln absichern.
