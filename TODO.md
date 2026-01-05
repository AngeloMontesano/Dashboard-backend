# TODO

## MUSS (kritisch)
- Admin: Logs-Tab in `AdminOperationsView` -> Backend-Endpoint anbinden (Tab aktuell ausgeblendet).
- Customer: Shell-Mobile-Breakpoints fertigstellen (<1100px umgesetzt); weitere Feinjustierung/Sidebar-Toggle optional prüfen.
- Customer: Reporting-PDF über API-Export statt DOM-Kopie (umgesetzt); Server-Export weiter verifizieren.
- Backend-Migration prüfen/ausführen: fehlende Tabellen `inventory_orders` und fehlerhafte Aggregation (GROUP BY) erzeugen 422/500 in Dashboard/Bestellungen/Inventur/Reporting.

## SOLL (UX/Konsistenz/Performance/Accessibility)
- Admin: Tenants/Memberships mit Server-Paging und Validierung (Settings-Form, Delete-Confirms über Dialog-Komponente) ausstatten.
- Admin: Theme-Toggle zusätzlich in der Topbar platzieren; Confirm-Dialog für Danger-Aktionen mit Fokus-Management nutzen.
- Customer: Queue-Operationen (Lagerbewegungen) mit Confirm für „Queue leeren“ und klaren Empty/Loading-States ergänzen.
- Customer: Einstellungen-Form validieren (Pflichtfelder, Busy/Disable pro Aktion), Test-E-Mail Feedback inline anzeigen.
- Customer: Bestellungen weiter verfeinern (Row-Busy ergänzt; leere Zustände/Fehler-Feedback weiter verbessern).
- Beide: Zentrale Fehler-Helfer (stringifyError) und einheitliche Toast/Overlay-Styles auf Token-Basis verwenden.

## KANN (Nice-to-have)
- Dashboard- und Reporting-KPIs serverseitig aggregieren, um Mehrfach-Requests/Caching zu vermeiden.
- Snapshot-Funktion (Admin) optional serverseitig speichern/teilen und Tenant/Host deutlich kennzeichnen.
- PrimeVue-Overlays/Charts an Theme-Tokens anpassen und A11y-Labels für Filter/Selects ergänzen.
