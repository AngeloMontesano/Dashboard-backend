# EPIC F – Offline Queue Fehlerhandling

## 1) Ziel
Endnutzerfreundliche Fehleroberfläche für die Offline Queue (IndexedDB) mit klarer Klassifizierung und Aktionen (Retry/Löschen).

## 2) Problem heute
- Fehler werden teils als Toast ausgegeben, keine zentrale Liste.
- Keine klare Klassifizierung (401/4xx/5xx/Netz) im UI.
- Entscheidungen (Retry/Löschen) fehlen für einzelne Queue-Einträge.

## 3) Scope
- Customer-Frontend Offline-Queue UX (Liste, Details, Aktionen).
- Fehlertexte gemäß Standard, keine Backend-Änderungen nötig.

## 4) Nicht-Ziele
- Keine neue Queue-Engine.
- Kein automatisches Retry-Konzeptänderung (nur UI-Steuerung).

## 5) User Journeys
- User öffnet „Sync-Probleme“: sieht Liste mit Status-Chips je Kategorie.
- User klickt Eintrag → Details mit HTTP-Status, Payload-Snippet, Timestamp.
- User wählt „Retry jetzt“ (einzelner Eintrag) oder „Löschen“; 401 zeigt CTA „Neu anmelden“.

## 6) UI/UX Regeln
- Tabs/Filter nach Kategorie (`auth`, `client`, `server`, `network`).
- Status-Badges: Wartet, Retry geplant, Blockiert, Anmeldung nötig.
- Keine Toast-Spam; dauerhafte Liste ist Quelle der Wahrheit.
- Klappbarer Technik-Block (Request-ID, Raw-Message).

## 7) API/Backend Annahmen
- Bestehende Queue-API/IndexedDB-Daten bleiben; Aktionen triggern vorhandene Retry/Delete-Funktionen.

## 8) Daten (konzeptionell)
- Queue Item: `{id, type, payload, status, lastError: {category, status, message, requestId?}, retries}`.
- Filter State: Kategorie + Textsuche.

### UX-Flow Liste + Detail (F-03)
- Einstieg: View „Sync-Probleme“ zeigt Tabs pro Kategorie (`auth`, `client`, `server`, `network`, `all`).
- Liste: Tabelle mit Spalten `Typ`, `Status-Badge`, `Letzter Fehler`, `Zeitpunkt`, `Aktionen (Retry/Löschen/Details)`.
- Status-Badges:
  - `auth`: „Anmeldung nötig“
  - `client` (4xx): „Blockiert“
  - `server` (5xx) / `network`: „Retry geplant“
  - `queued`: „Wartet“
- Filter: Textsuche über Request/Item-ID, Payload-Snippet; Tabs schalten Kategorie-Filter.
- Detail: Rechts-Drawer oder Modal mit Feldern `ID`, `Typ`, `Payload-Snippet`, `LastError` (Status, Kategorie, Message, Request-ID), `Retries`, `Zuletzt aktualisiert`.
- Aktionen im Detail: `Retry jetzt`, `Löschen`, bei `auth` zusätzlich „Neu anmelden“ (öffnet Login) und danach „Sync jetzt“.
- Fehlerdarstellung: Keine Toast-Spam, stattdessen Inline-Hinweis im Detail oder in der Liste; Technik-Block einklappbar.
- Busy/Retry: Buttons zeigen Spinner bei laufender Aktion; Auto-Retry-Status sichtbar („Retry läuft in Xs“ optional).
- Empty States: Pro Tab ein freundlicher Text („Keine Fehlversuche in dieser Kategorie“), CTA „Alle anzeigen“ (Tab `all`) oder „Erneut synchronisieren“.

### Komponentenstruktur (F-04)
- `QueueList` (Liste + Tabs + Filter)
  - Props: `items: QueueItem[]`, `activeTab: ErrorCategory`, `search: string`, `loading: boolean`
  - Emits: `update:activeTab`, `update:search`, `select(itemId)`, `retry(itemId)`, `remove(itemId)`
- `QueueItemRow`
  - Props: `item: QueueItem`, `compact: boolean`
  - Slots: `actions` (Retry/Löschen/Details)
- `QueueItemDetail` (Drawer/Modal)
  - Props: `item: QueueItem | null`, `open: boolean`, `busyAction?: 'retry' | 'remove'`
  - Emits: `close`, `retry(itemId)`, `remove(itemId)`, `login()`
- `QueueFilters`
  - Props: `categories: ErrorCategory[]`, `active: ErrorCategory`, `search: string`
  - Emits: `update:active`, `update:search`
- `QueueActions`
  - Props: `item: QueueItem`, `busy?: boolean`
  - Actions: `Retry`, `Löschen`, bei `auth` zusätzlich `Neu anmelden`
- Konvention: Alle Komponenten nutzen zentrale UI-Buttons/Badges, keine neuen Farben/Styles.

## 9) Tasks (umsetzbar, klein)
- **F-01** – Datenmodell der Queue-Einträge dokumentieren (bestehende Felder).  
  - Bereich: docs/customer  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: keine  
  - Done: Feldliste vorhanden.
- **F-02** – Fehlerklassifizierung mit `classifyError` abgleichen, Mapping definieren.  
  - Bereich: customer  
  - Dateien/Bereiche: `src/utils/errorClassify.ts` Nutzung  
  - Abhängigkeiten: F-01  
  - Done: Mapping-Tabelle erstellt.
- **F-03** – UX-Flow für Liste + Detail skizzieren (Tabs, Badges, Actions).  
  - Bereich: docs/ui  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: keine  
  - Done: Flow beschrieben.
- **F-04** – Komponentenstruktur planen (`QueueList`, `QueueItemDetail`, `QueueActions`).  
  - Bereich: customer  
  - Dateien/Bereiche: `components/queue/`  
  - Abhängigkeiten: F-03  
  - Done: Komponenten + Props definiert.
- **F-05** – Retry/Löschen-Aktionen gegen bestehende Queue-APIs verdrahten.  
  - Bereich: customer  
  - Dateien/Bereiche: Queue-Service  
  - Abhängigkeiten: F-04  
  - Done: Buttons triggern Service-Aufrufe.
- **F-06** – Auth-spezifische Aktion (Neu anmelden + Sync) dokumentieren.  
  - Bereich: customer  
  - Dateien/Bereiche: Epic Abschnitt, ggf. `useAuth` Integration  
  - Abhängigkeiten: F-02  
  - Done: Flow beschrieben.
- **F-07** – Fehlertexte/Empty States definieren (keine Einträge, gefilterte Liste).  
  - Bereich: docs/ui  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: keine  
  - Done: Texte final.
- **F-08** – QA-Checkliste (Retry/Delete, Kategorien, Offline) erstellen.  
  - Bereich: docs  
  - Dateien/Bereiche: QA-Abschnitt  
  - Abhängigkeiten: F-05  
  - Done: Prüfschritte notiert.
- **F-09** – Telemetrie-Ereignisse definieren (Retry Erfolg/Fehlschlag).  
  - Bereich: customer/docs  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: F-05  
  - Done: Events beschrieben.
- **F-10** – Accessibility-Prüfung (Focus-Reihenfolge, Aria-Labels) festlegen.  
  - Bereich: customer  
  - Dateien/Bereiche: Komponenten  
  - Abhängigkeiten: F-04  
  - Done: Anforderungen dokumentiert.

## 10) Akzeptanzkriterien
- Queue-Liste zeigt alle Fehler mit Kategorie/Status-Badges und Details.
- Retry und Löschen funktionieren pro Eintrag; 401 zeigt Login-Aktion.
- Keine Toast-Spam; Fehler bleiben in Liste nachvollziehbar.

## 11) Risiken/Offene Punkte
- IndexedDB-Konsistenz bei parallelen Writes.
- Große Payloads in Detailansicht müssen gekürzt werden.
- Retry-Strategie könnte mit Auto-Retry kollidieren.
