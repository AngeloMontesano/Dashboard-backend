# TODO

## MUSS (kritisch)
- Customer: Finale Dark-Mode-Visitenkontrolle und letzte UI-Politur (Artikel-Detailkarten/Empty-States); Light-Mode als Follow-up dokumentieren.
- Customer: Build-Qualität sicherstellen (`npm run build`) und Smoke-Tests im Dark-Mode; `rg "primevue"` muss 0 Treffer liefern.
- Docs: WORKLOG und Roadmap (`docs/roadmap/CUSTOMER_UI_PARITY_WITH_ADMIN.md`) aktuell halten; offene Paritätslücken dokumentieren.
- Backend (vorherige Lücken, weiterhin kritisch): Migration `0009_create_inventory_orders` ausrollen; Reporting-Query-Fix deployen; globale Stammdaten-/Industrie-Endpunkte und Admin-konforme Artikelrestriktionen ergänzen.
- Backend (Admin): System-Actions Endpoints mit echter Funktionalität hinterlegen (Cache Reset, Reindex, Restart) – aktuell bewusst nicht unterstützt (keine neuen Abhängigkeiten).
- Admin-Frontend Branchen ↔ Artikel: Zwei-Paneele-Editor mit serverseitiger Suche/Pagination und Pending-Add/Remove-Deltas implementieren; Speichern muss finalen Replace-Call (`IndustryArticlesUpdate.item_ids`) senden, da kein Delta-Endpunkt existiert.
- Admin-Frontend Branchen ↔ Artikel: Skalierungsfähiges Laden von Artikeln über `/admin/inventory/items` (Query q, category_id, active, page, page_size≤200) nutzen; Checkbox-Liste ersetzen und Ladezeiten/Scroll-Limitierungen eliminieren.
- Admin-Frontend Branchen ↔ Artikel: CSV/XLSX Import/Export fürs Mapping nur mit Backend-Unterstützung ermöglichen; solange Endpunkt fehlt, UI-Konzept dokumentieren und Backend-TODO für Delta-Import/Export anlegen.

## SOLL (UX/Konsistenz/Performance/Accessibility)
- Customer: Nach Input-/Empty-State-Harmonisierung Light/Dark-Regressionstests (Screenshots) und Responsiveness prüfen.
- Customer: Queue-/Bestell-Views mit klaren Busy/Confirm-Flows und konsistenter Button-Hierarchie ausstatten.
- Customer: Fehlermeldungen weiter verfeinern (Backend-spezifische Codes/Messages abbilden), Queue-/Auth-Event-Logs in zentrale Telemetrie einspeisen.
- Customer: DEV-Helfer nutzen, um `customer_auth_refresh_log` & `movement_queue_events` als JSON zu exportieren (Fehlerseite/Topbar Dev-Panel, import.meta.env.DEV).
- Admin/Customer: Gemeinsame Toast/Overlay-Styles auf Token-Basis konsolidieren und A11y-Labels für Filter/Selects ergänzen.
- Admin: Tenants/Memberships mit Server-Paging und Validierungen inkl. Confirm-Dialogen ausstatten; Theme-Toggle in Topbar ergänzen.
- Admin: Deployment-ENV für Build-/Commit-Infos setzen (APP_VERSION, GIT_COMMIT, BUILD_TIMESTAMP, BUILD_BRANCH, IMAGE_TAG), damit UI echte Werte zeigt.
- Admin (optional, nicht Teil dieser Aufgabe): Redis-gestütztes Caching und Cache-Reset-Endpunkt.
- Admin (optional, nicht Teil dieser Aufgabe): Such-/Index-Engine und Reindex-Endpunkt.
- Admin (optional, nicht Teil dieser Aufgabe): API-gestützter Restart-Hook (Orchestrator/Portainer/K8s).

## KANN (Nice-to-have)
- Customer/Admin: Serverseitige Aggregationen für KPIs/Reporting zur Reduktion von Requests/Caching-Bedarf.
- Customer: Snapshot/Export-Optionen für Dashboard/Reporting anbieten (Server-basiert, teilbar).
- Admin: Verbesserte Hinweise/Badges für Tenant/Host-Kontext und optionale Snapshot-Freigabe.
