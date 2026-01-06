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
| customer_frontend/customer-ui/src/components/reports/ReportFilters.vue:296-372 ↔ customer_frontend/customer-ui/src/styles/utilities.css:100-160 | Component-Scoped Form/Grid/Chip Styles vs. Utilities | Customer | Form/Grid/Chip/Hint erneut definiert, weichen nur in Gap-Werten minimal ab |
| customer_frontend/customer-ui/src/components/reports/ReportKpiCards.vue:65-103 ↔ admin_frontend/admin-ui/src/styles/utilities.css:348-374 | Component-Scoped Spinner/Grid vs. vorhandene Utilities | Customer | Spinner/Auto-fit-Grid doppelt, Werte leicht abweichend (Größe/Border) |
| customer_frontend/customer-ui/src/components/reports/ReportCharts.vue:148-193 ↔ customer_frontend/customer-ui/src/components/reports/ReportKpiCards.vue:65-103 | Component-Scoped Spinner/Grid/Placeholder | Customer | Zweiter Spinner + Grid/Layout nahezu identisch, nur andere Größen |
| customer_frontend/customer-ui/src/components/reports/ReportExportButtons.vue:35-45 ↔ customer_frontend/customer-ui/src/styles/utilities.css:54-74 | Component-Scoped Action-Row vs. Utilities | Customer | Flex/Gap/Wrap identisch zu section-actions/toolbar-group |
| customer_frontend/customer-ui/src/components/auth/AuthReauthBanner.vue:32-84 ↔ customer_frontend/customer-ui/src/styles/utilities.css:8-52 | Component-Scoped Banner/Actions vs. Section/Actions Utility | Customer | Padding/Border/Radius/Actions-Flex doppelt, nur leichte Abweichung bei Radius |
| customer_frontend/customer-ui/src/components/ui/UiEmptyState.vue:18-44 ↔ customer_frontend/customer-ui/src/styles/utilities.css:8-52 | Component-Scoped Empty-State vs. Section/Stack | Customer | Wiederholt Panel/Stack/Actions-Pattern, andere Border-Art (dashed) |
| customer_frontend/customer-ui/src/components/common/BaseField.vue:24-33 ↔ customer_frontend/customer-ui/src/styles/utilities.css:114-130 | Component-Scoped Hint/Error Colors vs. Text-Muted/Danger Utilities | Customer | Nutzt Legacy-Token `--color-*` statt der regulären Text-/Status-Tokens |
| customer_frontend/customer-ui/src/components/layout/Topbar.vue:65-97 ↔ customer_frontend/customer-ui/src/components/layout/Sidebar.vue:67-86 ↔ customer_frontend/customer-ui/src/styles/layout.css:300-356 | Badge/Counter Styles | Customer | Drei Varianten für Badges (Buttons/Nav) mit ähnlicher Typografie/Radius/Farben |

Notizen:
- Alle Fundstellen stammen aus Schritt 1 (Inventarisierung). Noch keine Deklaration wurde verändert.
- Design-Referenz laut Vorgabe: Admin-Frontend bleibt visuelle Referenz; Tokens laut docs/standards/THEME_TOKENS.md.
