# THEME TOKENS – Admin & Customer

## Zweck
Zentrale CSS-Variablen pro App, die sämtliche Farben, Abstände und Radii definieren. Views nutzen ausschließlich `var(--...)` aus `tokens.css`/`theme.css`.

## Muss-Felder je App (`src/styles/tokens.css`)
- **Surfaces & Layer**
  - `--surface-0` (Seitenhintergrund), `--surface-1` (Panels/Cards), `--surface-2` (Hover/Muted), `--overlay` (Masken/Glass).
- **Text**
  - `--text-strong`, `--text-muted`, `--placeholder`.
- **Accent & Status**
  - `--primary`, `--primary-strong`, `--success`, `--warning`, `--danger`, `--info`.
- **Border & Shadow**
  - `--border`, `--shadow-sm`, `--shadow-lg`.
- **Radius**
  - `--radius-sm`, `--radius-md`, `--radius-lg`.
- **Spacing Scale**
  - `--space-2`, `--space-4`, `--space-6`, `--space-8`, `--space-12`, `--space-16`, `--space-24`, `--space-32`.
- **Focus**
  - `--focus-ring` (outline/focus-shadow-Farbe).

## Light/Dark Vorgaben
- Light orientiert sich am Customer-Look: hellgraue Flächen auf Weiß, dezente Transparenzen, ruhiger Kontrast.
- Dark orientiert sich am Admin-Look: dunkle Basisflächen, klare Panel-Trennung, leicht transparente Cards mit erkennbarer Tiefe.
- Wertepaare je Theme-Variante definieren:
  - `:root { ... }` für Light.
  - `[data-theme="dark"] { ... }` für Dark (oder Klasse auf `<html>` wenn bereits etabliert).
  - Optional `[data-theme="system"]` mappt beim Init auf Light/Dark gemäß `matchMedia`.

## Mapping in `theme.css`
- Nutzt die Tokens, um konkrete UI-Flächen zu setzen:
  - Body/App-Hintergrund, Sidebar/Topbar/Section/Card-Flächen, Input/Toolbar-Hintergründe.
  - PrimeVue-Overrides (nur in der jeweiligen App) für Toast/Dialog/Overlay/Inputs.
- Keine neuen Farbwerte in `theme.css`, nur Token-Mapping/Komposition (z. B. `background: color-mix(...)` mit vorhandenen Tokens).

## Verwendung
- Views importieren nur `index.css`/`main.css`; dort werden `tokens.css` + `theme.css` + `utilities.css` eingebunden.
- Komponenten referenzieren ausschließlich Tokens (keine hex-Werte oder Pixel), Radii/Spacing kommen aus der Skala.
- Status-Badges/Tags nutzen Status-Tokens; Fokus-/Hover-Stati ebenfalls über Tokens (keine Inline-RGBA).

## PrimeVue (Customer)
- Lara-Preset bleibt Basis; `theme.css` ergänzt CSS-Variablen (z. B. `--p-surface-*`, `--p-text-*`) auf die lokalen Tokens.
- Keine per-Component-Overrides in Views; Anpassungen für Toast/Dialog/Overlay/Tooltip zentral in `theme.css`.

## Admin
- Bestehende Klassen (`.btnPrimary`, `.card`, `.table`, `.sidebar`, …) werden auf neue Tokens umgestellt.
- Dark-Mode-Varianten übernehmen dieselben Token-Namen; zusätzliche Themen (z. B. `theme-ocean`) können Token-Sets erweitern, aber Light/Dark bleiben Pflicht.
