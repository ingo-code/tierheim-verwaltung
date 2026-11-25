# Fachlichkeit – Tierheim

## Begriffe
- **Hund**: Tier im Bestand. Hat Name, Rasse (optional), Geburtsdatum (oft geschätzt), Geschlecht und Status.
- **Neuzugang**: Aufnahme eines Hundes, mit Aufnahmedatum und Herkunft (Fundtier, Abgabe, Beschlagnahme).
- **Chipnummer**: Transponder nach ISO 11784/11785, genau **15 Ziffern**. Die ersten 3 Ziffern sind ein
  Ländercode (Deutschland: 276) oder ein Herstellercode (900–999). Ein Hund kann bei der Aufnahme noch ohne Chip sein.
  Eine Chipnummer darf im Bestand nur **einmal** vorkommen.
- **Medikation**: Medikament, Dosis, Häufigkeit, Start- und (optional) Enddatum. Wichtig ist die Frage: Welche Hunde
  brauchen heute welches Medikament?
- **Status**: `aufgenommen` → `vermittelbar` → `reserviert` → `vermittelt` (oder `verstorben`, `zurück an Halter`).

## Erste Features (in dieser Reihenfolge)
1. Chipnummer prüfen (Wertobjekt)
2. Neuzugang erfassen (Use Case + In-Memory-Repository)
3. Doppelte Chipnummer verhindern
4. REST-API: Neuzugang anlegen, Bestand auflisten
5. Medikation hinzufügen, „heute fällig“ abfragen
6. Persistenz mit SQLite/SQLAlchemy
7. Next.js-Frontend: Bestandsliste, Neuzugangsformular, Medikamenten-Tagesliste
8. Bonus für ibb: CSV-Import und Report mit pandas
