# Admin UI Standards

## Stylesheet-Struktur (Admin)
Reihenfolge der Importe in `admin_frontend/admin-ui/src/main.ts`:
1. `styles/tokens.css` (Design Tokens)
2. `styles/base.css` (Reset/Typografie)
3. `styles/layout.css` (Layout-Primitives)
4. `styles/components.css` (Komponenten-Styles)
5. `styles/utilities.css` (Utilities)

## Design Tokens (tokens.css)
**Ziel:** Single Source of Truth für Farben, Abstände, Radius, Schatten und Inputs.

### Farb-Tokens
- Surfaces: `--surface-0` bis `--surface-3`, `--overlay`
- Text: `--text-strong`, `--text-muted`, `--placeholder`
- Status: `--primary`, `--success`, `--warning`, `--danger`, `--info`, `--neutral`
- Borders/Shadows: `--border`, `--shadow-sm`, `--shadow-md`, `--shadow-lg`

### Spacing & Radius
- Spacing Scale: `--space-2/3/4/6/8/10/12/16/24/32`
- Radius: `--radius-sm`, `--radius-md`, `--radius-lg`

### Input Tokens
- `--input-surface`, `--input-border`, `--input-focus`, `--input-placeholder`, `--input-text`

### Legacy Aliases
- `--bg`, `--panel`, `--surface`, `--surface2`, `--shadow`, `--shadow2`, `--ok`, `--bad` usw. bleiben erhalten,
  aber neue Styles bevorzugen die neuen Tokens.

## Layout-Primitives (layout.css)
- App-Shell: `.shell`, `.sidebar`, `.main`, `.topbar`
- Page-Container: `.page`
- Sections: `.section`, `.section-header`, `.section-title`, `.section-actions`
- Grid-Helper: `.grid1`, `.grid2`, `.grid-2`, `.grid3`, `.grid-auto`
- Breakpoints: `1100px` (Sidebar/Grids), `960px` (auto-fit), `900px` (Section/Padding)

## Komponenten-Styles (components.css)
- Buttons: `.btnPrimary`, `.btnGhost`, `.btnGhost.tiny`
- Inputs: `.input`, `.input.area`
- Cards: `.card`, `.cardHeader`, `.cardTitle`, `.cardHint`
- Status/Tags: `.statusPill`, `.statusDot`, `.tag`
- Tabellen: `.tableWrap`, `.table`
- Drawer/Toast: `.drawer`, `.drawerCard`, `.toastHost`

## Utilities (utilities.css)
**Layout:** `.u-row`, `.u-col`, `.u-gap-sm/md/lg`, `.u-actions-right`

**Spacing:** `.u-mt-*`, `.u-mb-*`, `.u-p-*` (siehe Spacing Scale)

**Text:** `.u-text-muted`, `.u-text-strong`, `.text-small`, `.text-muted`

**Forms:** `.u-field`, `.u-field-label`, `.u-field-control`

**Cards/Table:** `.u-card`, `.u-card-header`, `.u-card-body`, `.u-table-wrap`

## Regeln für neue Views
- Keine Inline-Styles; nutze Utilities oder generische Klassen.
- Keine neuen Scoped-Styles in Views ohne zwingenden Grund.
- Nutze `filter-card` + `two-column` für Filter-Layouts.
- Tabellen immer in `.tableWrap` + `.table`.
- Actions in `.action-row` oder `.toolbar` gruppieren.

## Responsive Regeln
- Verwende `grid-auto` oder `repeat(auto-fit, minmax(...))` für Card-Layouts.
- Filter/Toolbars müssen unter `960px` stapeln (Utility `two-column` erledigt das).
- File-Import-Actions nutzen `.row .wrap` und `.file-btn` für konsistente Button-Höhen.

## Theme Regeln
- Theme-State zentral über `src/theme/theme.ts`.
- `data-theme` wird auf `<html>` gesetzt (`light`/`dark`).
- Persistenz in `localStorage` (`admin_theme`), Fallback: System Preference.
- Views verwenden `useTheme()` für UI-Toggles.

## Login Background
- Der Login-Background liegt zentral in `src/styles/background/login.css` und ist mit dem Customer-Login abgestimmt.
- Login nutzt nur diesen Background (Aurora-Layer ist dort deaktiviert).
