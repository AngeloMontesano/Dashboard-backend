# EPIC E – Customer Orders Verbesserungen

## 1) Ziel
Bestellungen schneller erfassen: „Bestellwürdig“ vorausgefüllt, Dialog für mehrere Artikel ohne Fehlersignale, Storno-Konzept dokumentiert.

## 2) Problem heute
- Neue Bestellung startet ohne Vorbelegung, „Bestellwürdig“ wird vergessen.
- Dialog wirkt fehlerhaft durch rote Ränder/Fehleroptik.
- Keine Storno-Option dokumentiert.

## 3) Scope
- Prefill „Bestellwürdig“ beim Anlegen.
- Dialog für mehrere Artikel (tabellarisch, stapelbar) ohne aggressive Fehlerstyles.
- Konzept für Storno-Option (ohne Implementierung).

## 4) Nicht-Ziele
- Keine Änderungen an Backend-Order-Logik.
- Keine Payment-/Freigabeprozesse.

## 5) User Journeys
- User öffnet „Neue Bestellung“ → Tabellendialog mit leerer Zeile + Bestellwürdig-Filter aktiv.
- User fügt mehrere Artikel hinzu, Validierung zeigt Hinweise statt rote Ränder.
- User sieht Option „Storno beantragen“ (Konzept/Button disabled) mit Hinweis auf zukünftigen Flow.

## 6) UI/UX Regeln
- Formular-Validierung mit Inline-Hints, keine roten Rahmen vor Eingabe.
- Tabellarische Eingabe mit Add/Remove-Reihen, Tastaturnavigation möglich.
- Bestellwürdig-Filter im Hintergrund gesetzt, Badge sichtbar.

## 7) API/Backend Annahmen
- Bestehender Orders-Endpunkt unterstützt mehrere Items pro Request (vorhanden).
- Keine neuen Felder nötig.

## 8) Daten (konzeptionell)
- Prefill-Filter: `{reorderOnly: true}`.
- Dialog-Form: Liste von `{itemId, quantity, note?}` mit Frontend-Validierung.

## 9) Tasks (umsetzbar, klein)
- **E-01** – Prefill-Logik definieren (Quelle: Dashboard/CTA oder Standard).  
  - Bereich: customer  
  - Dateien/Bereiche: Bestellungen-View Logik  
  - Abhängigkeiten: keine  
  - Done: Regel dokumentiert.
- **E-02** – UI-Spezifikation für neuen Bestell-Dialog erstellen (Tabellen-Layout).  
  - Bereich: docs/ui  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: keine  
  - Done: Felder, Buttons, Fehlertexte beschrieben.
- **E-03** – Dialog-Komponente entwerfen (mehrere Zeilen, Add/Remove).  
  - Bereich: customer  
  - Dateien/Bereiche: neue Component unter `components/orders`  
  - Abhängigkeiten: E-02  
  - Done: Komponentengerüst geplant.
- **E-04** – Validierungsregeln festlegen (Pflichtfelder, Min/Max).  
  - Bereich: docs/customer  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: E-02  
  - Done: Regeln notiert.
- **E-05** – Fehlersicht ohne rote Ränder: Hint/Helper-Text definieren.  
  - Bereich: customer  
  - Dateien/Bereiche: Dialog-Komponente  
  - Abhängigkeiten: E-04  
  - Done: Styles/States geplant.
- **E-06** – Prefill „Bestellwürdig“ im Dialog aktivieren (Checkbox/Badge).  
  - Bereich: customer  
  - Dateien/Bereiche: Bestellungen-View, Dialog-State  
  - Abhängigkeiten: E-01  
  - Done: Prefill setzt Filter und markiert UI.
- **E-07** – Storno-Konzept dokumentieren (Status, Berechtigungen, UI-Entry).  
  - Bereich: docs/backend/customer  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: keine  
  - Done: Flow beschrieben.
- **E-08** – QA-Checkliste (Multi-Add, Prefill, Validierung) erstellen.  
  - Bereich: docs  
  - Dateien/Bereiche: QA-Abschnitt  
  - Abhängigkeiten: E-03–E-05  
  - Done: Tests gelistet.
- **E-09** – Accessibility-Prüfung (Keyboard, Screenreader-Labels) planen.  
  - Bereich: customer  
  - Dateien/Bereiche: Dialog-Komponente  
  - Abhängigkeiten: E-03  
  - Done: Anforderungen notiert.
- **E-10** – Telemetrie/Logging für Abbrüche/Fehler definieren (optional).  
  - Bereich: customer/docs  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: E-02  
  - Done: Events beschrieben.

## 10) Akzeptanzkriterien
- Neuer Bestell-Dialog erlaubt mehrere Artikel in einem Schritt ohne aggressive Fehleroptik.
- „Bestellwürdig“ wird beim Öffnen vorausgewählt und sichtbar gemacht.
- Storno-Option als Konzept sichtbar/dokumentiert (auch wenn disabled).

## 11) Risiken/Offene Punkte
- Usability bei vielen Zeilen (Scroll/Performance).
- Prefill könnte bestehende Filter-Persistenz überschreiben.
- Storno-Flow benötigt spätere Backend-Unterstützung.
