# Lernplan – Python-Bootcamp

| # | Lektion | Python-Thema | Status |
|---|---|---|---|
| 0 | Setup, leerer Test, erster Commit | uv, pytest, Pakete/Module | ✅ |
| 1 | Wertobjekt `Chipnummer` | Klassen, `@dataclass(frozen=True)`, Exceptions, `pytest.raises`, `parametrize`, `@classmethod`, `@property` | ✅ |
| 2 | Entität `Hund`, Use Case `NeuzugangErfassen` | Type Hints, `Enum`, `datetime.date`, `Protocol`, Fixtures, Test-Doubles | ✅ |
| 3 | In-Memory-Repository, doppelte Chips | dict, Dependency Injection von Hand, Vertragstests, `next()` mit Generator | ✅ |
| 4 | FastAPI: POST/GET | Pydantic-Modelle (≈ Zod), `TestClient`, `Depends`, Exception-Handler | ✅ |
| 5 | Medikation und „heute fällig“ | List Comprehensions (auch verschachtelt), Datumslogik `timedelta`, `%`, Sortieren mit Tupel-Key | ✅ |
| 6 | SQLite mit SQLAlchemy | ORM (`Mapped`, `relationship`), Sessions, `merge`, `tmp_path`, `monkeypatch`, App-Fabrik | ✅ |
| 7 | Next.js-Frontend | fetch gegen die API, CORS | ⬜ |
| 8 | pandas-Report/CSV-Import | DataFrames | ⬜ |

## Vorgehen mit dem Agenten (je Feature)
1. **Fachlich beschreiben:** „Ich will X, weil Y.“ Das Ergebnis kommt in `docs/`, wenn es neu ist.
2. **Test zuerst:** „Schreib mir den Test für X, noch keinen Code.“ Test lesen, verstehen und ausführen: **rot**.
3. **Minimal grün:** Selbst versuchen oder „Mach den Test grün, minimal.“ Dann `uv run pytest`: **grün**.
4. **Verstehen:** „Erklär mir Zeile für Zeile, was hier Python-typisch ist.“
5. **Refactor + Commit:** `git commit -m "feat(domain): ..."`
