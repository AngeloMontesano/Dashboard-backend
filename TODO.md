# TODO

## Must
- Legacy-Migration Backend: neue Admin-Metadaten für Einstellungen sind ergänzt; DB-Migration/Backfill für bestehende Tenants prüfen und ausrollen.
- Customer-Frontend: echte Daten für Inventur/Bestellungen/Einstellungen/Reporting sind verdrahtet; Feinschliff (Filter/Responsiveness/Tokens) fortführen.
- OpenAPI aktualisieren und Typen regenerieren, sobald neue Endpunkte implementiert sind; Wrapper auf neue Typen migrieren.
- Design-Tokens je App weiter verankern: neue Tokens in Utilities/Theme-Mappings nutzen und Alt-Variablen perspektivisch ablösen (admin: `src/styles/tokens.css`, customer: `src/styles/tokens.css`).
- Layout-Utilities/Ui-Komponenten sind angelegt (`src/styles/utilities.css`, `src/components/ui` je App); restliche Views schrittweise darauf umstellen, damit kein per-View Spacing/Styling verbleibt (Customer offen: Artikel/Berichte).
- Theme-Steuerung (System/Light/Dark) mit Persistenz + System-Listener ist eingebaut (`src/composables/useTheme.ts`, Admin-Sidebar/Settings, Customer-Topbar); Feinschliff und weitere Views/Overlays auf Tokens prüfen.
- Toast/Dialog/Overlay-Styles zentralisieren und per Tokens steuern (admin: `components/common/ToastHost.vue`, customer: PrimeVue-Overlay/Toast).

## Should
- Responsive-Regeln für Tabellen/Toolbars harmonisieren, damit mobile Ansichten nicht überlaufen (Customer: Dashboard/Lagerbewegungen/Berichte, Admin: Tenants/Users/Memberships/Operations).
- Inline-Styles, harte Farben/Pixel-Abstände aus Views entfernen, sobald Tokens/Utilities stehen (beide Frontends, besonders `src/views`).

## Could
- Gemeinsame Icon-/Eyebrow-Regeln für Sidebar/Topbar in beiden Apps ableiten, wenn Tokens/Utilities eingeführt sind.
- PrimeVue-Theming-Preselections (z. B. alternative Presets) evaluieren, falls Tokens nicht alle Komponentenflächen abdecken.
