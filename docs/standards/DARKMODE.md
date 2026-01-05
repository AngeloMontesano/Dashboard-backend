# DARK MODE – Umsetzungsvorgaben

## Ziel
Light/Dark-Modus identisch in beiden Frontends, Default folgt dem System. Persistenz in `localStorage`, Steuerung über `useTheme` pro App.

## Technische Umsetzung
- `src/composables/useTheme.ts` (je App)
  - Exportiert `theme` (ref) und Setter/Funktionen: `getTheme`, `setTheme`, `initTheme`.
  - Werte: `"light" | "dark" | "system"` (optional weitere Themes, aber Light/Dark Pflicht).
  - Persistenz: `localStorage.setItem('theme', value)` (App-spezifischer Key, z. B. `admin_theme`, `customer_theme`).
  - `initTheme` liest `localStorage`, sonst `matchMedia('(prefers-color-scheme: dark)')` für Default.
- Anwendung auf das DOM:
  - `document.documentElement.dataset.theme = 'light' | 'dark'`.
  - Für `system` wird beim Init auf Light/Dark gemappt, Dataset bleibt auf dem effektiven Wert.
  - Falls Klassen bereits genutzt werden (`theme-dark`), Mapping sauber kapseln, keine doppelten Klassen in Views.
- Integration in App-Bootstrap:
  - `main.ts` ruft `initTheme()` bevor `app.mount`.
  - PrimeVue erhält dieselben Variablen über `theme.css` (Customer).

## UI-Toggle
- Platzierung:
  - Admin: Sidebar/System-Bereich oder Topbar.
  - Customer: Topbar/Settings.
- Optionen: Light / Dark / System (oder Dropdown mit allen drei).
- Toggle nutzt Tokens für Farben/Spacing; keine Inline-Styles.

## Styling-Regeln
- Theme-Werte nur in `tokens.css`/`theme.css`.
- Keine per-View Farbwechsel; Views konsumieren Tokens über Utilities/UI-Bausteine.
- Fokus/Overlay/Toast-Styles passen sich automatisch über Tokens an (kein separater Codepfad).

## Tests/QA
- Manuelles Umschalten Light/Dark/System wechselt Hintergründe/Text/Panel sichtbar.
- Persistenz prüfen: Reload behält Auswahl.
- Mobile: Toggle zugänglich, Layout bricht nicht.
