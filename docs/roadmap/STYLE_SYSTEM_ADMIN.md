# Style System Admin → Customer (Plan)

## Ziel
Admin-Styles sind nun modularisiert und können 1:1 ins Customer-Frontend übernommen werden,
ohne Design-Neuentwicklung.

## Vorgehen (Plan)
1. **Styles kopieren**
   - `admin_frontend/admin-ui/src/styles/{tokens,base,layout,components,utilities}.css` nach `customer_frontend/customer-ui/src/styles/` übertragen.
   - Legacy-Aliasse im Customer-Frontend erhalten (Mapping beibehalten).
2. **Theme-Utility übernehmen**
   - `admin_frontend/admin-ui/src/theme/theme.ts` in Customer-Frontend spiegeln und `main.ts` darauf umstellen.
3. **Views anpassen**
   - Layout/Forms auf Utilities umstellen (`filter-card`, `tableWrap`, `action-row`).
   - Inline-Styles entfernen, `u-*` Utilities nutzen.
4. **QA/Build**
   - `npm run build` im Customer-Frontend.
   - Visuelle Smoke-Checks (Dark/Light/System).

## Abhängigkeiten
- Kein PrimeVue-Zuwachs (keine neuen Abhängigkeiten).
- Keine Änderungen an Customer-Logik, nur Styles/Theme.
