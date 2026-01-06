# Error Handling (Frontend)

Kurzer Leitfaden für kundenfreundliche Fehleroberflächen und Queue-Probleme im Customer-Frontend.

## Klassifizierung
- Utility: `src/utils/errorClassify.ts`
- Kategorien: `auth`, `client`, `server`, `network`, `unknown`
- Regeln:
  - `401` → `auth`, User-Text: „Sitzung abgelaufen. Bitte neu anmelden.“
  - `400/404/405/409/422` → `client`, verständliche Kurztexte ohne HTTP-Slang.
  - `>=500` → `server`, User-Text: „Server nicht erreichbar oder Fehler im System.“
  - Keine Antwort/Timeout → `network`, User-Text: „Keine Verbindung. Wir versuchen es erneut.“
  - Detailtexte nur im Technik-Block zeigen.

## UI-Prinzipien
- Keine rohen Axios-/HTTP-Fehler im sichtbaren UI.
- Dauerhafte Fehlerübersicht statt Toast-Spam: Badge in Sidebar/Topbar, Seite „Fehlgeschlagene Buchungen“ mit Liste + Details.
- Status-Chips: „Wartet“ (queued), „Retry geplant“ (5xx/Netz), „Blockiert“ (4xx), „Anmeldung nötig“ (401).
- Technische Details optional einklappbar (HTTP-Status, Raw-Message, Request-ID falls vorhanden).

## Aktionen pro Kategorie
- `auth` (401): „Neu anmelden“ → Login, danach „Sync jetzt“.
- `client` (4xx): „Bearbeiten“ (prefill) oder „Löschen“ (kein Auto-Retry).
- `server`/`network`: „Jetzt erneut versuchen“ + Auto-Retry aktiv lassen.
- Manuelle Retry-Buttons senden nur den gewählten Queue-Eintrag.

## Toast-Regeln
- Fehler primär in der Fehlerliste anzeigen, keine wiederholten Fehler-Toast-Spams.
- Wenn Toast nötig: höchstens einmal pro Session je Fehlertyp (`onceKey` in `useToast`), sonst still.
- Erfolgstoasts optional; sie dürfen ausgeblendet werden, wenn die Liste die Quelle der Wahrheit ist.
