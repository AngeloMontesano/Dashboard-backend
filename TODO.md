# TODO

## MUSS (kritisch)
- Customer: Finale Dark-Mode-Visitenkontrolle und letzte UI-Politur (Artikel-Detailkarten/Empty-States); Light-Mode als Follow-up dokumentieren.
- Customer: Build-Qualität sicherstellen (`npm run build`) und Smoke-Tests im Dark-Mode; `rg "primevue"` muss 0 Treffer liefern.
- Docs: WORKLOG und Roadmap (`docs/roadmap/CUSTOMER_UI_PARITY_WITH_ADMIN.md`) aktuell halten; offene Paritätslücken dokumentieren.
- Backend (vorherige Lücken, weiterhin kritisch): Migration `0009_create_inventory_orders` ausrollen; Reporting-Query-Fix deployen; globale Stammdaten-/Industrie-Endpunkte und Admin-konforme Artikelrestriktionen ergänzen.

## SOLL (UX/Konsistenz/Performance/Accessibility)
- Customer: Filter-/Form-Controls auf Admin-Input-Pattern (Pills, Focus-Ring) vereinheitlichen; Table-Leer-States harmonisieren.
- Customer: Queue-/Bestell-Views mit klaren Busy/Confirm-Flows und konsistenter Button-Hierarchie ausstatten.
- Customer: Queue-Fehler-Formularvalidierung und Feld-Hints im Fehlerzentrum nachschärfen (Barcode/Qty/Note).
- Customer: Fehlermeldungen weiter verfeinern (Backend-spezifische Codes/Messages abbilden), Monitoring/Telemetry für Queue-Aktionen ergänzen.
- Customer: Einheitliches Auth-Handling (401/403) in allen Views/Datenladepfaden ausrollen, inkl. Redirect/CTA und Bannern ohne HTTP-Slang.
- Admin/Customer: Gemeinsame Toast/Overlay-Styles auf Token-Basis konsolidieren und A11y-Labels für Filter/Selects ergänzen.
- Admin: Tenants/Memberships mit Server-Paging und Validierungen inkl. Confirm-Dialogen ausstatten; Theme-Toggle in Topbar ergänzen.
- Admin: System-Actions (Cache Reset/Reindex) fehlen als Endpunkte und UI; bei Settings-Refactor nur Hinweise/Platzhalter möglich, Backend-Bereitstellung klären.
- Admin: Backend-Build-/Version-Infos fehlen; UI zeigt nur App-Version aus package.json/VITE_BUILD_INFO. Serverseitige Build/Commit-Quelle ergänzen.

## KANN (Nice-to-have)
- Customer/Admin: Serverseitige Aggregationen für KPIs/Reporting zur Reduktion von Requests/Caching-Bedarf.
- Customer: Snapshot/Export-Optionen für Dashboard/Reporting anbieten (Server-basiert, teilbar).
- Admin: Verbesserte Hinweise/Badges für Tenant/Host-Kontext und optionale Snapshot-Freigabe.
