# OpenAPI Types

## Warum generieren?
- Einheitliche Request-/Response-Typen aus der API-Spezifikation verhindern Drift zwischen Frontend und Backend.
- Die generierten Typen dienen als einzige Quelle für Payload-Formate in zentralen API-Wrappern.

## Generierung
- `npm run gen:types` nutzt `https://api.test.myitnetwork.de/openapi.json` als Single Source of Truth.
- Die generierte Datei landet je Frontend unter `src/api/gen/openapi.ts`.
- Lokale Kopien werden nicht als Quelle für die Typgenerierung verwendet.

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
- Neue Endpunkte zuerst im zentralen OpenAPI unter `https://api.test.myitnetwork.de/openapi.json` pflegen, dann Typen regenerieren.

## Known Issues
- Backend muss die aktualisierten OpenAPI-Definitionen (Login, Items-Import/Export, Movements, Set-Password, Reporting) bestätigen, damit die generierten Typen zur Laufzeit passen.
