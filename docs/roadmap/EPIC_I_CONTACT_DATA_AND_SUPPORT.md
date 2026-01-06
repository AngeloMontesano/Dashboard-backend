# EPIC I – Kontakt­daten & Support

## 1) Ziel
Globale Firmenkontaktdaten im Admin pflegen, tenant-spezifische Vertriebs­kontakte in Kunden-Details speichern, Anzeige im Customer-Frontend (Einstellungen/Hilfe).

## 2) Problem heute
- Keine zentrale Pflege globaler Kontakte.
- Vertriebs-Kontakt je Tenant nicht erfasst.
- Customer-Frontend zeigt keine Support-/Kontaktinfos.

## 3) Scope
- Admin-Einstellungen: globale Firma/Support-Kontaktfelder.
- Tenant-Details: Vertriebs-Kontaktfelder.
- Customer-Frontend: Anzeige der Kontakte in Einstellungen/Hilfe.

## 4) Nicht-Ziele
- Keine Ticketing-/Support-Automation.
- Keine E-Mail-Versandlogik.

## 5) User Journeys
- Admin pflegt globale Kontaktdaten (Firma, Telefon, E-Mail, Support-URL) in Einstellungen.
- Admin pflegt pro Tenant Vertriebs-Kontakt (Name, Telefon, E-Mail) in Kunden-Details.
- Customer öffnet Einstellungen/Hilfe und sieht beide Blöcke (global + tenant-spezifisch).

## 6) UI/UX Regeln
- Pflichtfelder klar markiert; Validierung auf E-Mail/Telefon-Format.
- Anzeige im Customer-UI als kontaktierbare Links, klare Labels.
- Fallback: Wenn tenant-spezifisch fehlt, nur globale Daten anzeigen.

## 7) API/Backend Annahmen
- Admin-Endpunkte für globale Einstellungen erweitern um Kontaktfelder.
- Tenant-Settings-Endpunkt erweitert um Vertriebs-Kontaktfelder.
- Customer-Settings-Endpunkt liefert beide Blöcke kombiniert.

## 8) Daten (konzeptionell)
- Global: `{company_name, support_email, support_phone, support_url}`.
- Tenant-spezifisch: `{sales_contact_name, sales_contact_email, sales_contact_phone}`.
- Customer-Response: `{global_contact, tenant_contact}`.

## 9) Tasks (umsetzbar, klein)
- **I-01** – Felddefinitionen dokumentieren (Validierung, Optionalität).  
  - Bereich: docs/backend  
  - Dateien/Bereiche: Epic Abschnitt, openapi  
  - Abhängigkeiten: keine  
  - Done: Tabelle mit Feldern/Regeln vorhanden.
- **I-02** – Backend-Schema/Endpoints für globale Kontakte planen.  
  - Bereich: backend  
  - Dateien/Bereiche: admin settings router, models  
  - Abhängigkeiten: I-01  
  - Done: Migration/Schema-Plan notiert.
- **I-03** – Tenant-Settings um Vertriebs-Kontakt erweitern (Plan).  
  - Bereich: backend  
  - Dateien/Bereiche: tenant_settings routes/model  
  - Abhängigkeiten: I-01  
  - Done: Felder/Validierung beschrieben.
- **I-04** – Admin-UI Formulare für globale Kontakte entwerfen.  
  - Bereich: admin  
  - Dateien/Bereiche: Einstellungen-View  
  - Abhängigkeiten: I-02  
  - Done: UI-Felder/Helpertexte skizziert.
- **I-05** – Admin-UI Tenant-Details um Vertriebs-Kontaktfelder ergänzen (Plan).  
  - Bereich: admin  
  - Dateien/Bereiche: Tenant-Detail Forms  
  - Abhängigkeiten: I-03  
  - Done: Layout/Validierung dokumentiert.
- **I-06** – Customer-Frontend Anzeige/Settings konzipieren (Hilfebereich).  
  - Bereich: customer  
  - Dateien/Bereiche: Einstellungen/Hilfe View  
  - Abhängigkeiten: I-02, I-03  
  - Done: Anzeigeplan mit Links.
- **I-07** – API-Client/Models erweitern (Admin + Customer) Planung.  
  - Bereich: admin/customer  
  - Dateien/Bereiche: API-Wrapper  
  - Abhängigkeiten: I-02  
  - Done: Typenfelder aufgelistet.
- **I-08** – QA-Checkliste (Validierung, Fallback, Anzeige) erstellen.  
  - Bereich: docs  
  - Dateien/Bereiche: QA-Abschnitt  
  - Abhängigkeiten: I-04–I-06  
  - Done: Prüfschritte notiert.
- **I-09** – Datenschutz/Visibility-Notizen ergänzen (wer sieht was).  
  - Bereich: docs  
  - Dateien/Bereiche: Epic Abschnitt  
  - Abhängigkeiten: I-01  
  - Done: Sichtbarkeitsregeln dokumentiert.

## 10) Akzeptanzkriterien
- Felddefinitionen und API-Erweiterungen dokumentiert.
- Admin-UI- und Customer-UI-Konzepte für Kontaktanzeige klar beschrieben.
- QA-Plan deckt Validierung und Fallbacks ab.

## 11) Risiken/Offene Punkte
- Datenschutz bei Anzeige der Vertriebs-Kontakte klären.
- Migration bestehender Daten nötig.
- Mehrsprachigkeit der Texte ggf. erforderlich.
