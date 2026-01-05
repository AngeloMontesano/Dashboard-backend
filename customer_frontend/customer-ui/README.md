# Customer Frontend (Customer UI)

## Smoke-Checkliste
- Login mit gültigen Tenant-Zugangsdaten durchführen. In den DevTools prüfen, dass API-Calls direkt gegen `https://api.<baseDomain>` (ohne zusätzliches `/api`-Prefix) laufen und die Konsole keine Fehler wirft.
- Nach dem Login zur Artikelverwaltung wechseln: Kategorien und Artikel sollen ohne Auth-Fehler geladen werden.
- Button „Neuer Artikel“ anklicken: Modal öffnet sich, Pflichtfelder (SKU, Name, Barcode, Einheit) ausfüllen, speichern und prüfen, dass der Artikel in der Liste erscheint.
- Button „Import CSV“ anklicken: Modal öffnet sich, Datei auswählen, Mapping Schritt erreichen und Import starten; Ergebnis (erstellt/aktualisiert/Fehler) wird angezeigt.
