# TODO

## MUSS (kritisch)
- Customer: Finale Dark-Mode-Visitenkontrolle und letzte UI-Politur (Artikel-Detailkarten/Empty-States); Light-Mode als Follow-up dokumentieren.
- Customer: Build-Qualität sicherstellen (`npm run build`) und Smoke-Tests im Dark-Mode; `rg "primevue"` muss 0 Treffer liefern.
- Docs: WORKLOG und Roadmap (`docs/roadmap/CUSTOMER_UI_PARITY_WITH_ADMIN.md`) aktuell halten; offene Paritätslücken dokumentieren.
- Backend (vorherige Lücken, weiterhin kritisch): Migration `0009_create_inventory_orders` ausrollen; Reporting-Query-Fix deployen; globale Stammdaten-/Industrie-Endpunkte und Admin-konforme Artikelrestriktionen ergänzen.
- Backend (Admin): System-Actions Endpoints mit echter Funktionalität hinterlegen (Cache Reset, Reindex, Restart) – aktuell bewusst nicht unterstützt (keine neuen Abhängigkeiten).
- Admin-Frontend Branchen ↔ Artikel: Backend-API für CSV/XLSX Mapping-Import/Export (Delta Add/Remove) bereitstellen; UI aktuell ohne Buttons, da OpenAPI keine Endpunkte kennt.
- Admin-Frontend Branchen ↔ Artikel: Aggregierte Info für Überschneidungen (z. B. „in X Branchen“) per API liefern, damit Badge ohne N+1-Calls gerendert werden kann; aktuell nur Single-Branchen-Items vorhanden.
- Admin-Frontend Branchen ↔ Artikel: Remote-OpenAPI (2026-01-06) bestätigt weiterhin nur GET/PUT für `/admin/inventory/industries/{industry_id}/items` ohne Import/Export oder Overlap; Backend-Implementierung bleibt Blocker.
- SMTP/Mail (Admin/Tenant): Migration `0013_add_use_tls_to_system_email_settings` ausrollen, Staging-Tests für `/admin/smtp/settings[*]`, `/inventory/settings/test-email` und `/inventory/orders/{order_id}/email` fahren; Logs mit `request_id`/TLS-Status prüfen.
- Admin UI SMTP: Manuelle E2E-Tests des neuen SMTP-Abschnitts (Speichern, Passwort-Update, Testmail) gegen Staging; Request-ID/Fehlerdetails im UI sichtbar halten.

## Next
- [A-08] (EPIC_A_TENANT_RESOLUTION) Status-Caching/Retry-Strategie umsetzen.
- [B-06] (EPIC_B_GLOBAL_CATALOG_AND_INDUSTRY) View „Globale Artikel“ inkl. Branche/Typ planen.
- [C-05] (EPIC_C_CUSTOMER_REPORTING_UX) Zeitraum-Presets + freie Datumauswahl definieren.
- [D-04] (EPIC_D_CUSTOMER_DASHBOARD_NAVIGATION) Bestellungen-View Prefill für offene/Bestellwürdig vorbereiten.
- [E-06] (EPIC_E_CUSTOMER_ORDERS_IMPROVEMENTS) Prefill „Bestellwürdig“ im Dialog aktivieren.
- [F-05] (EPIC_F_OFFLINE_QUEUE_ERROR_HANDLING) Retry/Löschen gegen Queue-APIs verdrahten.
- [G-05] (EPIC_G_DOCUMENTATION_AND_HELP) Help-Button Konzept Customer dokumentieren.
- [H-03] (EPIC_H_MONITORING_LIGHTWEIGHT) Statische Statusseite entwerfen.
- [I-02] (EPIC_I_CONTACT_DATA_AND_SUPPORT) Backend-Schema/Endpoints für globale Kontakte planen.

## Later
- [B-10] (EPIC_B_GLOBAL_CATALOG_AND_INDUSTRY) Verteilungskonzept an Tenants dokumentieren.
- [C-09] (EPIC_C_CUSTOMER_REPORTING_UX) Export-Konzept festlegen.
- [D-08] (EPIC_D_CUSTOMER_DASHBOARD_NAVIGATION) QA-Checkliste Navigation erstellen.
- [E-07] (EPIC_E_CUSTOMER_ORDERS_IMPROVEMENTS) Storno-Konzept dokumentieren.
- [F-09] (EPIC_F_OFFLINE_QUEUE_ERROR_HANDLING) Telemetrie-Ereignisse definieren.
- [G-08] (EPIC_G_DOCUMENTATION_AND_HELP) QA-Checkliste (Links, Rollen, Sichtbarkeit) erstellen.
- [H-07] (EPIC_H_MONITORING_LIGHTWEIGHT) QA/Smoke-Plan für Statusseite ausarbeiten.
- [I-08] (EPIC_I_CONTACT_DATA_AND_SUPPORT) QA-Checkliste für Kontakte erstellen.
