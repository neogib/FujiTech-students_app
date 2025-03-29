import logging
from typing import Any

from sqlmodel import Session, select

from ..app.core.database import engine
from ..app.models.locations import Gminy, Miejscowosci, Powiaty, Ulice, Wojewodztwa
from ..app.models.schools import (
    EtapyEdukacji,
    StatusPublicznoprawny,
    Szkoly,
    SzkolyEtapyLink,  # noqa: F401
    TypySzkol,
)

logger = logging.getLogger(__name__)


class DatabaseDecomposer:
    def __init__(self):
        self.engine = engine
        self.session: Session | None = None
        self.wojewodztwa_cache = {}
        self.powiaty_cache = {}
        self.gminy_cache = {}
        self.miejscowosci_cache = {}
        self.ulice_cache = {}
        self.typy_szkol_cache = {}
        self.statusy_cache = {}
        self.etapy_edukacji_cache = {}

    def __enter__(self):
        # Create the session when entering the context
        self.session = Session(self.engine)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the session when exiting the context
        self.close()

    def _ensure_session(self) -> Session:
        """Ensure we have an active session and return it"""
        if self.session is None:
            self.session = Session(self.engine)
        return self.session

    def _get_or_create_wojewodztwo(self, nazwa: str, teryt: str) -> Wojewodztwa:
        session = self._ensure_session()
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.wojewodztwa_cache:
            return self.wojewodztwa_cache[cache_key]

        wojewodztwo = session.exec(
            select(Wojewodztwa).where(Wojewodztwa.teryt == teryt)
        ).first()

        if not wojewodztwo:
            wojewodztwo = Wojewodztwa(nazwa=nazwa, teryt=teryt)

        self.wojewodztwa_cache[cache_key] = wojewodztwo
        return wojewodztwo

    def _get_or_create_powiat(
        self, nazwa: str, teryt: str, wojewodztwo: Wojewodztwa
    ) -> Powiaty:
        session = self._ensure_session()
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.powiaty_cache:
            return self.powiaty_cache[cache_key]

        powiat = session.exec(select(Powiaty).where(Powiaty.teryt == teryt)).first()

        if not powiat:
            powiat = Powiaty(nazwa=nazwa, teryt=teryt, wojewodztwo=wojewodztwo)

        self.powiaty_cache[cache_key] = powiat
        return powiat

    def _get_or_create_gmina(self, nazwa: str, teryt: str, powiat: Powiaty) -> Gminy:
        session = self._ensure_session()
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.gminy_cache:
            return self.gminy_cache[cache_key]

        gmina = session.exec(select(Gminy).where(Gminy.teryt == teryt)).first()

        if not gmina:
            gmina = Gminy(nazwa=nazwa, teryt=teryt, powiat=powiat)

        self.gminy_cache[cache_key] = gmina
        return gmina

    def _get_or_create_miejscowosc(
        self, nazwa: str, teryt: str, gmina: Gminy
    ) -> Miejscowosci:
        session = self._ensure_session()
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.miejscowosci_cache:
            return self.miejscowosci_cache[cache_key]

        miejscowosc = session.exec(
            select(Miejscowosci).where(Miejscowosci.teryt == teryt)
        ).first()

        if not miejscowosc:
            miejscowosc = Miejscowosci(nazwa=nazwa, teryt=teryt, gmina=gmina)

        self.miejscowosci_cache[cache_key] = miejscowosc
        return miejscowosc

    def _get_or_create_ulica(
        self, nazwa: str, teryt: str
    ) -> Ulice | None:  # Using pipe operator
        if not nazwa or not teryt:
            return None

        session = self._ensure_session()
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.ulice_cache:
            return self.ulice_cache[cache_key]

        ulica = session.exec(select(Ulice).where(Ulice.teryt == teryt)).first()

        if not ulica:
            ulica = Ulice(nazwa=nazwa, teryt=teryt)

        self.ulice_cache[cache_key] = ulica
        return ulica

    def _get_or_create_typ_szkoly(self, nazwa: str) -> TypySzkol:
        session = self._ensure_session()
        if nazwa in self.typy_szkol_cache:
            return self.typy_szkol_cache[nazwa]

        typ_szkoly = session.exec(
            select(TypySzkol).where(TypySzkol.nazwa == nazwa)
        ).first()

        if not typ_szkoly:
            typ_szkoly = TypySzkol(nazwa=nazwa)

        self.typy_szkol_cache[nazwa] = typ_szkoly
        return typ_szkoly

    def _get_or_create_status(self, nazwa: str) -> StatusPublicznoprawny:
        session = self._ensure_session()
        if nazwa in self.statusy_cache:
            return self.statusy_cache[nazwa]

        status = session.exec(
            select(StatusPublicznoprawny).where(StatusPublicznoprawny.nazwa == nazwa)
        ).first()

        if not status:
            status = StatusPublicznoprawny(nazwa=nazwa)

        self.statusy_cache[nazwa] = status
        return status

    def _get_or_create_etap_edukacji(self, nazwa: str) -> EtapyEdukacji:
        session = self._ensure_session()
        if nazwa in self.etapy_edukacji_cache:
            return self.etapy_edukacji_cache[nazwa]

        etap = session.exec(
            select(EtapyEdukacji).where(EtapyEdukacji.nazwa == nazwa)
        ).first()

        if not etap:
            etap = EtapyEdukacji(nazwa=nazwa)

        self.etapy_edukacji_cache[nazwa] = etap
        return etap

    def prune_and_decompose_single_school_data(
        self, school_data: dict[str, Any]
    ) -> None:
        session = self._ensure_session()

        # Check if school already exists
        existing_school = session.exec(
            select(Szkoly).where(Szkoly.numer_rspo == school_data["numerRspo"])
        ).first()

        if existing_school:
            logger.info(
                f"School with RSPO {school_data['numerRspo']} already exists. Skipping."
            )
            return

        # Process location hierarchy
        wojewodztwo = self._get_or_create_wojewodztwo(
            nazwa=school_data["wojewodztwo"], teryt=school_data["wojewodztwoKodTERYT"]
        )

        powiat = self._get_or_create_powiat(
            nazwa=school_data["powiat"],
            teryt=school_data["powiatKodTERYT"],
            wojewodztwo=wojewodztwo,
        )

        gmina = self._get_or_create_gmina(
            nazwa=school_data["gmina"],
            teryt=school_data["gminaKodTERYT"],
            powiat=powiat,
        )

        miejscowosc = self._get_or_create_miejscowosc(
            nazwa=school_data["miejscowosc"],
            teryt=school_data["miejscowoscKodTERYT"],
            gmina=gmina,
        )

        ulica = None
        if "ulica" in school_data and "ulicaKodTERYT" in school_data:
            ulica = self._get_or_create_ulica(
                nazwa=school_data["ulica"], teryt=school_data["ulicaKodTERYT"]
            )

        # Process school type
        typ = self._get_or_create_typ_szkoly(nazwa=school_data["typ"]["nazwa"])

        # Process school status
        status = self._get_or_create_status(
            nazwa=school_data["statusPublicznoPrawny"]["nazwa"]
        )

        # Process education stages
        etapy = []
        for etap_data in school_data.get("etapyEdukacji", []):
            etap = self._get_or_create_etap_edukacji(nazwa=etap_data["nazwa"])
            etapy.append(etap)

        # Create new school
        geolokalizacja = school_data.get("geolokalizacja", {})

        # using get method when parameter can be None, otherwise using [] operator
        new_school = Szkoly(
            numer_rspo=school_data["numerRspo"],
            nip=school_data.get("nip"),
            regon=school_data["regon"],
            liczba_uczniow=school_data.get("liczbaUczniow"),
            nazwa=school_data["nazwa"],
            dyrektor_imie=school_data.get("dyrektorImie"),
            dyrektor_nazwisko=school_data.get("dyrektorNazwisko"),
            geolokalizacja_latitude=geolokalizacja.get("latitude"),
            geolokalizacja_longitude=geolokalizacja.get("longitude"),
            kod_pocztowy=school_data["kodPocztowy"],
            numer_budynku=school_data.get("numerBudynku"),
            numer_lokalu=school_data.get("numerLokalu"),
            telefon=school_data.get("telefon"),
            email=school_data.get("email"),
            strona_internetowa=school_data.get("stronaInternetowa"),
            # relationships
            typ=typ,
            status=status,
            miejscowosc=miejscowosc,
            ulica=ulica,
            etapy=etapy,
        )

        session.add(new_school)
        session.commit()
        session.refresh(new_school)

        logger.info(f"Added school: {new_school.nazwa} (RSPO: {new_school.numer_rspo})")

    def prune_and_decompose_schools(self, schools_data: list[dict[str, Any]]) -> None:
        for school_data in schools_data:
            try:
                self.prune_and_decompose_single_school_data(school_data)
            except Exception as e:
                logger.error(
                    f"Error processing school, RSPO: {school_data.get('numerRspo', 'unknown')}, name: {school_data.get('nazwa', 'unknown')}, error: {e}"
                )
                session = self._ensure_session()
                session.rollback()

    def close(self):
        """
        Manual close method for when not using as context manager
        """
        if self.session:
            self.session.close()
            self.session = None
