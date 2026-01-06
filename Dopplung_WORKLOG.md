## Doppelungen – Erstinventur (Schritt 1)

| Fundstelle (Datei:Zeilen) | Art | Admin / Customer | Bewertung |
| --- | --- | --- | --- |
| admin_frontend/admin-ui/src/styles/tokens.css:10-85 ↔ customer_frontend/customer-ui/src/styles/tokens.css:10-85 | Token-Set Light/Dark (Surfaces, Text, Accent, Spacing) | beide | Identische Werte; doppelte Pflege nötig |
| admin_frontend/admin-ui/src/styles/base.css:12-44 ↔ customer_frontend/customer-ui/src/styles/base.css:12-44 | Globale Basis (body/app Hintergrund & Text) | beide | Gleiches Ziel (Grundfläche/Textfarbe), unterschiedliche Token-Namen |
| admin_frontend/admin-ui/src/styles/layout.css:8-127 ↔ customer_frontend/customer-ui/src/styles/layout.css:8-127 | Layout-Klassen (Shell/Sidebar/Nav) | beide | Werte sehr ähnlich (Radius/Shadow/Surface), Paralleldefinition |
| admin_frontend/admin-ui/src/styles/layout.css:231-325 ↔ customer_frontend/customer-ui/src/styles/layout.css:231-325 | Layout-Klassen (Card/Input/Status/Buttons) | beide | Semantisch gleich, padding/shadow/Input-Tokens leicht differierend |
| admin_frontend/admin-ui/src/styles/utilities.css:8-122 ↔ customer_frontend/customer-ui/src/styles/utilities.css:8-122 | Utility-Klassen (page/section/section-header/chip/filter) | beide | Gleiches Muster, unterschiedliche Token-Zuordnung (panel vs surface-1) |
| admin_frontend/admin-ui/src/App.vue:581-644 ↔ admin_frontend/admin-ui/src/styles/layout.css:8-140 | Component-Scoped Overrides vs. globale Layout-Klassen | Admin | App.vue überschreibt Shell/Sidebar/Nav trotz gleicher Klassennamen |
| admin_frontend/admin-ui/src/components/users/UserCreateCard.vue:64-96 ↔ admin_frontend/admin-ui/src/styles/utilities.css:70-122 | Component-Scoped Form-Layout vs. Utilities | Admin | FormGrid/Field/Label/Actions erneut definiert, nur minimale Abweichungen |
| customer_frontend/customer-ui/src/styles/layout.css:436-486 ↔ customer_frontend/customer-ui/src/styles/utilities.css:8-156 | Compatibility-Layer Klassen vs. aktuelle Utilities | Customer | Legacy-Klassen duplizieren aktuelle Utility-/Layout-Patterns (Grid, Buttons, Badges) |

Notizen:
- Alle Fundstellen stammen aus Schritt 1 (Inventarisierung). Noch keine Deklaration wurde verändert.
- Design-Referenz laut Vorgabe: Admin-Frontend bleibt visuelle Referenz; Tokens laut docs/standards/THEME_TOKENS.md.
