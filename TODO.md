# TODO

## MUSS (kritisch)
- Admin: Logs-Tab in `AdminOperationsView` liefert nur Demo-Daten (TODO-Kommentar) → echten Endpoint anbinden oder Tab bis Verfügbarkeit ausblenden.
- Admin: Auth-Kontext (adminKey/actor) wird nicht persistiert; Reload führt zum Logout → sichere Persistenz (session/localStorage) ergänzen.
- Customer: Shell ohne Mobile-Breakpoints (Sidebar fix 260px) → Sidebar/Toolbar für <1100px stacken oder toggeln, um abgeschnittene Inhalte zu vermeiden.
- Customer: Reporting-PDF nutzt `window.open` + DOM-Kopie → Popup-Blocker und fehlendes Theming; auf Server-Export oder tokenisiertes Client-PDF umstellen.
- Customer: Bestellungen-Aktionen (PDF/E-Mail/Status) ohne Row-Busy/Disable → Doppel-Aktionen verhindern, Fehler pro Zeile anzeigen.

## SOLL (UX/Konsistenz/Performance/Accessibility)
- Admin: Tenants/Memberships mit Server-Paging und Validierung (Settings-Form, Delete-Confirms über Dialog-Komponente) ausstatten.
- Admin: Theme-Toggle zusätzlich in der Topbar platzieren; Confirm-Dialog für Danger-Aktionen mit Fokus-Management nutzen.
- Customer: Queue-Operationen (Lagerbewegungen) mit Confirm für „Queue leeren“ und klaren Empty/Loading-States ergänzen.
- Customer: Einstellungen-Form validieren (Pflichtfelder, Busy/Disable pro Aktion), Test-E-Mail Feedback inline anzeigen.
- Beide: Zentrale Fehler-Helfer (stringifyError) und einheitliche Toast/Overlay-Styles auf Token-Basis verwenden.

## KANN (Nice-to-have)
- Dashboard- und Reporting-KPIs serverseitig aggregieren, um Mehrfach-Requests/Caching zu vermeiden.
- Snapshot-Funktion (Admin) optional serverseitig speichern/teilen und Tenant/Host deutlich kennzeichnen.
- PrimeVue-Overlays/Charts an Theme-Tokens anpassen und A11y-Labels für Filter/Selects ergänzen.
