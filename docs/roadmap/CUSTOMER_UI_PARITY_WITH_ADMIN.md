# Customer UI Parity mit Admin-Frontend

Ziel: Customer-Frontend optisch/strukturell 1:1 an Admin-Frontend angleichen und PrimeVue vollständig entfernen. Backend bleibt unverändert; Proxy auf `/api` bleibt bestehen.

## Phasen & Meilensteine

1. **Inventur & Plan** (abgeschlossen)
   - PrimeVue-Nutzung und Styles im Customer erfassen.
   - Admin-Styles (Tokens/Base/Layout/Utilities) als Quelle der Wahrheit identifizieren.
   - Paritäts-Checkliste erstellen (dieses Dokument), TODO priorisieren, WORKLOG fortschreiben.

2. **Design-System übernehmen**
   - Admin-Tokens/Base/Layout/Utilities nach `customer_frontend/customer-ui/src/styles` übernehmen.
   - Token-Kompatibilität sicherstellen (bestehende Farb-/Spacing-Variablen aliasen).
   - App-Shell/Grundflächen auf Admin-Dark-Optik bringen.

3. **PrimeVue entfernen**
   - Dependencies/Plugins/Imports/CSS-Overrides löschen.
   - PrimeVue-Komponenten ersetzen (Dropdown/MultiSelect/Calendar/DataTable/Dialog/Toast/etc.) durch leichte, Admin-stylische Alternativen.
   - Eigenes Toast-System im Admin-Look verwenden.

4. **Views angleichen**
   - Dashboard, Artikelverwaltung, Kategorien, Lagerbewegungen, Inventur, Berichte, Bestellungen, Einstellungen: Cards/Buttons/Inputs/Tabellen auf Admin-Pattern heben.
   - Filterleisten, KPIs, Tabellen-Header/-Hover/-Active States, Empty States auf Admin-Design abstimmen.

5. **Qualitätssicherung**
   - `rg "primevue"` == 0 im Customer.
   - `npm run build` erfolgreich.
   - Dark-Mode visuell wie Admin, Light-Mode später nachziehen.
   - WORKLOG/TODO aktuell; offene Lücken dokumentiert.

## Checkliste (Stand laufend aktualisieren)
- [x] Admin-Styles (tokens/base/layout/utilities) im Customer eingebunden.
- [x] Token-Aliaising für bestehende Customer-Klassen vorhanden.
- [x] App-Shell (Sidebar/Topbar/Main) wirkt wie Admin.
- [x] PrimeVue Dependencies/Plugins/Imports entfernt.
- [x] PrimeVue-Komponenten durch Admin-Stil-Alternativen ersetzt (inkl. Toast).
- [x] Reporting-Filter/Charts/Tables ohne PrimeVue funktionsfähig.
- [x] Tabellen/Card/Buttons/Input-Styling identisch zu Admin-Dark (Basis + Kompatibilitätslayer).
- [x] `npm run build` Customer erfolgreich.
- [ ] Dark-Mode visuell geprüft; Light-Mode TODO erfasst.
- [x] WORKLOG/TODO aktualisiert.
