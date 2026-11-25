"""HundRepository mit SQLite über SQLAlchemy 2.

Die Tabellen-Klassen (`HundZeile`, `MedikationZeile`) sind bewusst getrennt von den
Domain-Klassen: Die Domain kennt keine Datenbank. Übersetzt wird nur hier,
in `_zu_zeile` und `_zu_hund`.
"""

from datetime import date
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKey, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from tierheim.domain.chipnummer import Chipnummer
from tierheim.domain.hund import Geschlecht, Herkunft, Hund, Status
from tierheim.domain.medikation import Medikation


class Base(DeclarativeBase):
    pass


class HundZeile(Base):
    __tablename__ = "hunde"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    geschlecht: Mapped[str]
    herkunft: Mapped[str]
    aufnahmedatum: Mapped[date]
    rasse: Mapped[str | None]
    chipnummer: Mapped[str | None] = mapped_column(unique=True, index=True)
    status: Mapped[str]
    medikationen: Mapped[list["MedikationZeile"]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="MedikationZeile.reihenfolge",
    )


class MedikationZeile(Base):
    __tablename__ = "medikationen"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    hund_id: Mapped[UUID] = mapped_column(ForeignKey("hunde.id"), index=True)
    reihenfolge: Mapped[int]
    medikament: Mapped[str]
    dosis: Mapped[str]
    startdatum: Mapped[date]
    enddatum: Mapped[date | None]
    intervall_tage: Mapped[int]


class SqliteHundRepository:
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self._sessions = sessions

    @classmethod
    def fuer_url(cls, url: str) -> Self:
        """Erzeugt Engine und Tabellen, z. B. `sqlite:///tierheim.db`."""
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        return cls(sessionmaker(engine, expire_on_commit=False))

    def speichern(self, hund: Hund) -> None:
        with self._sessions.begin() as session:
            session.merge(_zu_zeile(hund))

    def finde_per_id(self, hund_id: UUID) -> Hund | None:
        with self._sessions() as session:
            zeile = session.get(HundZeile, hund_id)
            return _zu_hund(zeile) if zeile else None

    def finde_per_chip(self, chipnummer: Chipnummer) -> Hund | None:
        with self._sessions() as session:
            zeile = session.scalars(
                select(HundZeile).where(HundZeile.chipnummer == chipnummer.wert)
            ).first()
            return _zu_hund(zeile) if zeile else None

    def alle(self) -> list[Hund]:
        with self._sessions() as session:
            return [_zu_hund(zeile) for zeile in session.scalars(select(HundZeile))]


# --- Übersetzung Domain ⇄ Tabelle --------------------------------------------------


def _zu_zeile(hund: Hund) -> HundZeile:
    return HundZeile(
        id=hund.id,
        name=hund.name,
        geschlecht=hund.geschlecht.value,
        herkunft=hund.herkunft.value,
        aufnahmedatum=hund.aufnahmedatum,
        rasse=hund.rasse,
        chipnummer=hund.chipnummer.wert if hund.chipnummer else None,
        status=hund.status.value,
        medikationen=[
            MedikationZeile(
                id=m.id,
                hund_id=hund.id,
                reihenfolge=position,
                medikament=m.medikament,
                dosis=m.dosis,
                startdatum=m.startdatum,
                enddatum=m.enddatum,
                intervall_tage=m.intervall_tage,
            )
            for position, m in enumerate(hund.medikationen)
        ],
    )


def _zu_hund(zeile: HundZeile) -> Hund:
    return Hund(
        id=zeile.id,
        name=zeile.name,
        geschlecht=Geschlecht(zeile.geschlecht),
        herkunft=Herkunft(zeile.herkunft),
        aufnahmedatum=zeile.aufnahmedatum,
        rasse=zeile.rasse,
        chipnummer=Chipnummer(zeile.chipnummer) if zeile.chipnummer else None,
        status=Status(zeile.status),
        medikationen=[
            Medikation(
                id=m.id,
                medikament=m.medikament,
                dosis=m.dosis,
                startdatum=m.startdatum,
                enddatum=m.enddatum,
                intervall_tage=m.intervall_tage,
            )
            for m in zeile.medikationen
        ],
    )
