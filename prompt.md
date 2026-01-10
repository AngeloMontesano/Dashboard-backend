WICHTIG:
- Nur lesen und analysieren
- KEINE Codeänderungen
- KEINE Annahmen
- Nur das dokumentieren, was im Repository tatsächlich existiert

AUFGABE:
Erstelle eine technische Entwickler-Dokumentation für dieses Repository.

VORGEHEN:
1. Lege einen neuen Ordner /dokumentation an.
2. Erstelle die Datei /dokumentation/Dokumentation.index.md als Einstieg.
3. Analysiere das Projekt schrittweise und dokumentiere nacheinander:


PERSISTENZ:
- Lege /dokumentation an, falls nicht vorhanden
- Erstelle /dokumentation/prompt.md und speichere diesen Prompt dort
- Erstelle /dokumentation/todo.md als Arbeitsliste
- Lies vor jeder Arbeit zuerst todo.md
- Aktualisiere todo.md nach jedem abgeschlossenen Schritt

TODO-MANAGEMENT:
- todo.md enthält:
  - offene Punkte
  - erledigte Punkte (mit Datum)
  - nächste empfohlene Schritte

ARBEITSWEISE:
1. Prüfe todo.md
2. Arbeite exakt einen Punkt ab
3. Dokumentiere das Ergebnis in der passenden .md Datei
4. Aktualisiere todo.md
5. Beende den Schritt sauber

STRUKTUR DER DOKUMENTATION:
/dokumentation
  ├─ Dokumentation.index.md
  ├─ backend.md
  ├─ api.md
  ├─ datenbank.md
  ├─ konfiguration.md
  ├─ todo.md
  └─ prompt.md


- backend.md
  - Zweck des Backends
  - Einstiegspunkte
  - Hauptmodule
  - Zusammenspiel der Komponenten

- api.md
  - Übersicht aller API-Endpunkte dokumentation/openapi.json.
  - HTTP-Methode, Pfad, Zweck
  - Kurzbeschreibung der Logik
  - Welche Komponenten sie nutzen

- datenbank.md
  - Datenmodelle
  - Tabellen / Entitäten
  - Beziehungen
  - Zweck der wichtigsten Felder

- konfiguration.md
  - Relevante Konfigurationsdateien
  - Umgebungsvariablen
  - Start- und Laufzeitverhalten

STIL:
- Technisch
- Sachlich
- Entwickler-orientiert
- Markdown
- Klare Überschriften
- Keine Marketing-Sprache
- Keine Wiederholungen

WICHTIG:
- Arbeite auf Basis der Repo-Map und lade Dateien gezielt nach
- Dokumentiere nur, was eindeutig aus dem Code hervorgeht
- Wenn etwas unklar ist, kennzeichne es explizit als „nicht ersichtlich“

BEGINNE MIT:
- Anlegen des Ordners /dokumentation
- Erstellen von Dokumentation.index.md
- Initialer Eintrag in todo.md:
  - Projektstruktur analysieren
  - Dokumentation.index.md erstellen
  
- Danach die Analyse der Top-Level-Ordner
