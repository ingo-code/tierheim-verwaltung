# Fachlichkeit – Tierheim

## Begriffe
- **Hund**: Tier im Bestand. Hat Name, Rasse (optional), Geburtsdatum (oft geschätzt), Geschlecht und Status.
- **Neuzugang**: Aufnahme eines Hundes, mit Aufnahmedatum und Herkunft (Fundtier, Abgabe, Beschlagnahme).
- **Chipnummer**: Transponder nach ISO 11784/11785, genau **15 Ziffern**. Die ersten 3 Ziffern sind ein
  Ländercode 001–899 (Deutschland: 276; Auslandshunde z. B. Rumänien 642) oder ein Herstellercode (900–999);
  000 ist ungültig. Eingaben mit Leerzeichen („276 098 100 123 456“) werden bereinigt. Ein Hund kann bei der Aufnahme noch ohne Chip sein.
  Eine Chipnummer darf im Bestand nur **einmal** vorkommen.
- **Medikation**: Medikament, Dosis, Startdatum, optionales Enddatum (inklusive) und Intervall in Tagen
  (1 = täglich, 7 = wöchentlich). Fällig ist sie an jedem Tag im Zeitraum, an dem (Tag − Start) durch das Intervall
  teilbar ist. **Tagesliste**: alle heute fälligen Gaben der Hunde, die noch im Heim sind (nicht `vermittelt`),
  sortiert nach Hund und Medikament.
- **Status**: `aufgenommen` → `vermittelbar` → `reserviert` → `vermittelt` (oder `verstorben`, `zurück an Halter`).

## Erste Features (in dieser Reihenfolge)
1. Chipnummer prüfen (Wertobjekt)
2. Neuzugang erfassen (Use Case + In-Memory-Repository)
3. Doppelte Chipnummer verhindern
4. REST-API: Neuzugang anlegen, Bestand auflisten
5. Medikation hinzufügen, „heute fällig“ abfragen
6. Persistenz mit SQLite/SQLAlchemy
7. Next.js-Frontend: Bestandsliste, Neuzugangsformular, Medikamenten-Tagesliste
8. CSV-Import und Report mit pandas

## CSV-Format (Import und Export)
Trennzeichen `;`, Kopfzeile `Name;Geschlecht;Herkunft;Aufnahmedatum;Rasse;Chipnummer` (Export zusätzlich `Status`).
Datum `TT.MM.JJJJ`, Geschlecht `Rüde`/`Hündin`, Herkunft `Fundtier`/`Abgabe`/`Beschlagnahme`.
Kodierung UTF-8 (mit/ohne BOM) oder Windows-1252. Fehlerhafte Zeilen werden mit Zeilennummer gemeldet, der Rest importiert.
Beispiel: `beispieldaten/bestand.csv` (7 gültige, 2 absichtlich fehlerhafte Zeilen).
Offen: Der Import übernimmt die Spalte `Status` noch nicht (importierte Hunde sind `aufgenommen`).

## Bestandsreport
Im Heim = alle außer `vermittelt`. Kennzahlen: Anzahl im Heim, Verteilung nach Status (alle) und Herkunft (im Heim),
durchschnittliche Verweildauer in Tagen, die 3 längsten Aufenthalte, Hunde ohne Chip, heute fällige Gaben.
