# EPIC D – Customer Dashboard Navigation

## 1) Ziel
KPI-Karten im Customer-Dashboard sind klickbar und führen zu den passenden Detailseiten.

## 2) Problem heute
- KPI-Karten sind statisch, keine direkte Navigation.
- Nutzer springen über Sidebar statt Kontext-Link.

## 3) Scope
- Customer-Dashboard KPI-Karten: Offene Bestellungen → Bestellungen, Bewegungen heute → Lagerbewegungen, Bestellwürdig → Bestellungen mit Filter.
- Routing- und UI-Verhalten festlegen.

## 4) Nicht-Ziele
- Keine neuen KPIs oder Berechnungen.
- Keine zusätzlichen Filter im Ziel-View außer prefill.

## 5) User Journeys
- User klickt „Offene Bestellungen“ → landet in Bestellungen-View mit Filter `status=open` gesetzt.
- User klickt „Bewegungen heute“ → Lagerbewegungen-View mit Datum=heute.
- User klickt „Bestellwürdig“ → Bestellungen-View mit Tab/Filter „Bestellwürdig“ vorausgewählt.

## 6) UI/UX Regeln
- KPI-Karten erhalten Hover/Active-State, ganze Karte klickbar.
- Fokus-Ring für Tastatur, `role=button` + `aria-label`.
- Optionaler Hinweis im Tooltip, wohin navigiert wird.

## 7) API/Backend Annahmen
- Keine neuen Endpunkte nötig; bestehende Views liefern Filter-Optionen.

## 8) Daten (konzeptionell)
- Prefill-Filter: `{status: 'open'}`, `{date: today}`, `{reorderOnly: true}`.
- State-Transfer über Router-Query oder globalen Store.

### Klick-Logik (D-03)
- Komponenten: `UiStatCard` erhält Props `to` (RouteLocationRaw), `prefill` (optional Filterobjekt), `aria-label`.
- Navigation: `router.push({ name: <route>, query: prefillQuery })`, `prefillQuery` baut aus obigen Prefill-Objekten (z. B. `status=open`, `date=today`, `reorderOnly=true`).
- Ziele:
  - Offene Bestellungen → Route `bestellungen` mit `status=open`.
  - Bewegungen heute → Route `lagerbewegungen` mit `date=today`.
  - Bestellwürdig → Route `bestellungen` mit `reorderOnly=true`.
- UX:
  - Ganze Karte klickbar (`role="button"`, `tabindex="0"`), `aria-label` mit Zielbeschreibung.
  - Hover/Active-State per Tokens, Fokus-Ring sichtbar.
  - Tooltip optional: „Zur Bestellungen mit Filter …“.
- Fehlerfälle:
  - Wenn Router-Navigation fehlschlägt, einmalige Toast/Hint („Navigation nicht möglich“), kein Spam.

## 9) Tasks (umsetzbar, klein)
- **D-01** – Ziel-Routen und Filterparameter festlegen.  
  - Bereich: docs/customer  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: keine  
  - Done: Tabelle Route→Filter vorhanden.
- **D-02** – Router-Interface für Prefill definieren (Query/State).  
  - Bereich: customer  
  - Dateien/Bereiche: `src/router/index.ts` Konzept  
  - Abhängigkeiten: D-01  
  - Done: Vorgehen dokumentiert.
- **D-03** – KPI-Komponente klickbar machen (button/link).  
  - Bereich: customer  
  - Dateien/Bereiche: `src/components/dashboard/`  
  - Abhängigkeiten: D-02  
  - Done: Karten navigieren, Fokus-Ring vorhanden.
- **D-04** – Bestellungen-View akzeptiert Prefill für offene/Bestellwürdig.  
  - Bereich: customer  
  - Dateien/Bereiche: `BestellungenView`  
  - Abhängigkeiten: D-02  
  - Done: Query-Parameter setzen Filter initial.
- **D-05** – Lagerbewegungen-View akzeptiert Prefill Datum=heute.  
  - Bereich: customer  
  - Dateien/Bereiche: `LagerbewegungenView`  
  - Abhängigkeiten: D-02  
  - Done: Initialfilter angewandt.
- **D-06** – Tooltip/Hint auf KPI-Karten ergänzen.  
  - Bereich: customer  
  - Dateien/Bereiche: Dashboard-Komponenten  
  - Abhängigkeiten: D-03  
  - Done: Hover-Hinweis sichtbar.
- **D-07** – Accessibility-Check (Keyboard/Screenreader).  
  - Bereich: customer  
  - Dateien/Bereiche: Dashboard-Komponenten  
  - Abhängigkeiten: D-03  
  - Done: Tab-Reihenfolge korrekt, `aria-label` gesetzt.
- **D-08** – QA-Checkliste für Navigation erstellen.  
  - Bereich: docs  
  - Dateien/Bereiche: Epic QA-Abschnitt  
  - Abhängigkeiten: D-04, D-05  
  - Done: Liste vorhanden.

## 10) Akzeptanzkriterien
- Alle drei KPI-Karten navigieren in die vorgesehenen Views mit vorgefüllten Filtern.
- Keyboard-Navigation funktioniert, Fokus sichtbar.
- Keine unerwarteten Filterpersistenzen nach Rücksprung.

## 11) Risiken/Offene Punkte
- Prefill darf lokale Filterpersistenz nicht überschreiben (falls vorhanden).
- Query-basierte Prefills müssen mit bestehenden Bookmarks kompatibel bleiben.
