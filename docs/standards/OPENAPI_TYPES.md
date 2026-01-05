# OpenAPI Types

## Warum generieren?
- Einheitliche Request-/Response-Typen aus der API-Spezifikation verhindern Drift zwischen Frontend und Backend.
- Die generierten Typen dienen als einzige Quelle für Payload-Formate in zentralen API-Wrappern.

## Generierung
- Remote: `npm run gen:types` (nutzt `https://api.test.myitnetwork.de/openapi.json`).
- Lokal: `npm run gen:types:local` (nutzt `docs/openapi/openapi.json`).
- Die generierte Datei landet je Frontend unter `src/api/gen/openapi.ts`.
- `docs/openapi/openapi.json` enthält die referenzierte Spezifikation im Repository.

## Nutzung in Wrappern (Beispiele)
- Admin Tenants:
  ```ts
  import type { paths } from "./gen/openapi";
  type TenantListResponse = paths["/admin/tenants"]["get"]["responses"]["200"]["content"]["application/json"];
  const tenants = await api.get<TenantListResponse>("/admin/tenants", config);
  ```
- Customer Inventory Items:
  ```ts
  import type { components, paths } from "./gen/openapi";
  type ItemsPage = components["schemas"]["ItemsPage"];
  type ItemsQuery = NonNullable<paths["/inventory/items"]["get"]["parameters"]["query"]>;
  const res = await api.get<ItemsPage>("/inventory/items", { params, headers });
  ```

## Regeln
- `src/api/gen/openapi.ts` wird nicht manuell editiert.
- Wrapper nutzen die generierten Typen für Requests (Payload) und Responses (Resultate).
- Neue Endpunkte zuerst in `docs/openapi/openapi.json` bzw. Remote-Schema pflegen, dann Typen regenerieren.

## Known Issues
- Remote-Schema `https://api.test.myitnetwork.de/openapi.json` liefert aus der aktuellen Umgebung HTTP 403; Typen werden daher aus der lokal abgelegten Kopie generiert.
- `/admin/login` Response ist im Schema als `Record<string, never>` definiert; tatsächlich wird `{ admin_key, actor? }` erwartet.
- `/inventory/items/import` und `/inventory/items/export` sind im Schema als leere Objekte (`Record<string, never>`) beschrieben; aktuelle Wrapper benötigen detailreiche Felder (imported/updated/errors bzw. `{ csv: string }`).
- `/inventory/movements` Response ist als `unknown` beschrieben; Wrapper gehen von einem verwertbaren Response-Body aus.
- Der Endpoint `/admin/tenants/{tenant_id}/users/{user_id}/set-password` fehlt im Schema; der Wrapper nutzt weiterhin den bisherigen Pfad und erwartet eine Tenant-User-Rückgabe.
- Reporting-Endpunkte (`/inventory/report`, `/inventory/reports/consumption`, `/inventory/reports/export/{format}`) fehlen im Schema; der Frontend-Fallback aggregiert derzeit Bewegungen clientseitig.
