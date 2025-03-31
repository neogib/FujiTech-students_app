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

    def close(self):
        """Manual close method for when not using as context manager"""
        if self.session:
            self.session.close()
            self.session = None

    def _ensure_session(self) -> Session:
        """Ensure we have an active session and return it"""
        if self.session is None:
            self.session = Session(self.engine)
        return self.session

    def _missing_required_key(
        self, school_data: dict[str, Any], e: Exception, required_key: str
    ):
        logger.error(
            f"""❌ Missing required {required_key} data for school:
                - RSPO: {school_data.get("numerRspo", "unknown")},
                - name: {school_data.get("nazwa", "unknown")}, 
                - error: {e}"""
        )
        self._ensure_session().rollback()

    def _select_where(self, model, condition):
        session = self._ensure_session()
        return session.exec(select(model).where(condition)).first()

    def _get_or_create_wojewodztwo(self, nazwa: str, teryt: str) -> Wojewodztwa:
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.wojewodztwa_cache:
            return self.wojewodztwa_cache[cache_key]

        wojewodztwo = self._select_where(Wojewodztwa, Wojewodztwa.teryt == teryt)

        if not wojewodztwo:
            wojewodztwo = Wojewodztwa(nazwa=nazwa, teryt=teryt)

        self.wojewodztwa_cache[cache_key] = wojewodztwo
        return wojewodztwo

    def _get_or_create_powiat(
        self, nazwa: str, teryt: str, wojewodztwo: Wojewodztwa
    ) -> Powiaty:
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.powiaty_cache:
            return self.powiaty_cache[cache_key]

        powiat = self._select_where(Powiaty, Powiaty.teryt == teryt)

        if not powiat:
            powiat = Powiaty(nazwa=nazwa, teryt=teryt, wojewodztwo=wojewodztwo)

        self.powiaty_cache[cache_key] = powiat
        return powiat

    def _get_or_create_gmina(self, nazwa: str, teryt: str, powiat: Powiaty) -> Gminy:
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.gminy_cache:
            return self.gminy_cache[cache_key]

        gmina = self._select_where(Gminy, Gminy.teryt == teryt)

        if not gmina:
            gmina = Gminy(nazwa=nazwa, teryt=teryt, powiat=powiat)

        self.gminy_cache[cache_key] = gmina
        return gmina

    def _get_or_create_miejscowosc(
        self, nazwa: str, teryt: str, gmina: Gminy
    ) -> Miejscowosci:
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.miejscowosci_cache:
            return self.miejscowosci_cache[cache_key]

        miejscowosc = self._select_where(Miejscowosci, Miejscowosci.teryt == teryt)

        if not miejscowosc:
            miejscowosc = Miejscowosci(nazwa=nazwa, teryt=teryt, gmina=gmina)

        self.miejscowosci_cache[cache_key] = miejscowosc
        return miejscowosc

    def _get_or_create_ulica(self, nazwa: str, teryt: str) -> Ulice | None:
        if not nazwa or not teryt:
            return None

        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.ulice_cache:
            return self.ulice_cache[cache_key]

        ulica = self._select_where(Ulice, Ulice.teryt == teryt)

        if not ulica:
            ulica = Ulice(nazwa=nazwa, teryt=teryt)

        self.ulice_cache[cache_key] = ulica
        return ulica

    def _get_or_create_typ_szkoly(self, nazwa: str) -> TypySzkol:
        if nazwa in self.typy_szkol_cache:
            return self.typy_szkol_cache[nazwa]

        typ_szkoly = self._select_where(TypySzkol, TypySzkol.nazwa == nazwa)

        if not typ_szkoly:
            typ_szkoly = TypySzkol(nazwa=nazwa)

        self.typy_szkol_cache[nazwa] = typ_szkoly
        return typ_szkoly

    def _get_or_create_status(self, nazwa: str) -> StatusPublicznoprawny:
        if nazwa in self.statusy_cache:
            return self.statusy_cache[nazwa]

        status = self._select_where(
            StatusPublicznoprawny, StatusPublicznoprawny.nazwa == nazwa
        )

        if not status:
            status = StatusPublicznoprawny(nazwa=nazwa)

        self.statusy_cache[nazwa] = status
        return status

    def _get_or_create_etap_edukacji(self, nazwa: str) -> EtapyEdukacji:
        if nazwa in self.etapy_edukacji_cache:
            return self.etapy_edukacji_cache[nazwa]

        etap = self._select_where(EtapyEdukacji, EtapyEdukacji.nazwa == nazwa)

        if not etap:
            etap = EtapyEdukacji(nazwa=nazwa)

        self.etapy_edukacji_cache[nazwa] = etap
        return etap

    def prune_and_decompose_single_school_data(
        self, school_data: dict[str, Any]
    ) -> None:
        session = self._ensure_session()
        try:
            # Check if school already exists
            existing_school = self._select_where(
                Szkoly, Szkoly.numer_rspo == school_data["numerRspo"]
            )

            if existing_school:
                logger.info(
                    f"🔙 School with RSPO {school_data['numerRspo']} already exists. Skipping."
                )
                return

            # Process location hierarchy
            try:
                wojewodztwo = self._get_or_create_wojewodztwo(
                    nazwa=school_data["wojewodztwo"],
                    teryt=school_data["wojewodztwoKodTERYT"],
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
            except KeyError as e:
                self._missing_required_key(school_data, e, "location")
                return

            # Process school type
            try:
                typ = self._get_or_create_typ_szkoly(nazwa=school_data["typ"]["nazwa"])
                status = self._get_or_create_status(
                    nazwa=school_data["statusPublicznoPrawny"]["nazwa"]
                )
            except KeyError as e:
                self._missing_required_key(school_data, e, "type or status")
                return

            # Process education stages
            try:
                etapy = []
                for etap_data in school_data.get("etapyEdukacji", []):
                    etap = self._get_or_create_etap_edukacji(nazwa=etap_data["nazwa"])
                    etapy.append(etap)
            except KeyError as e:
                self._missing_required_key(school_data, e, "education stage")
                return

            # Create new school
            try:
                geolokalizacja = school_data["geolokalizacja"]

                # using get method when parameter can be None, adding or None to assign None if parameter is ""
                # when parameter is required using [] operator
                new_school = Szkoly(
                    numer_rspo=school_data["numerRspo"],
                    nip=school_data.get("nip") or None,
                    regon=school_data["regon"],
                    liczba_uczniow=school_data.get(
                        "liczbaUczniow"
                    ),  # here no "or None" because I want to leave 0 as a value
                    nazwa=school_data["nazwa"],
                    dyrektor_imie=school_data.get("dyrektorImie") or None,
                    dyrektor_nazwisko=school_data.get("dyrektorNazwisko") or None,
                    geolokalizacja_latitude=geolokalizacja["latitude"],
                    geolokalizacja_longitude=geolokalizacja["longitude"],
                    kod_pocztowy=school_data["kodPocztowy"],
                    numer_budynku=school_data.get("numerBudynku") or None,
                    numer_lokalu=school_data.get("numerLokalu") or None,
                    telefon=school_data.get("telefon") or None,
                    email=school_data.get("email") or None,
                    strona_internetowa=school_data.get("stronaInternetowa") or None,
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
                logger.info(
                    f"💾 Added school: {new_school.nazwa} (RSPO: {new_school.numer_rspo})"
                )

            except KeyError as e:
                self._missing_required_key(school_data, e, "school")
                return

        except Exception as e:
            logger.error(
                f"❌ Unexpected error processing school {school_data.get('numerRspo', 'unknown')}: {e}"
            )
            session.rollback()
            return

    def prune_and_decompose_schools(self, schools_data: list[dict[str, Any]]) -> None:
        """
        Process a list of schools data
        """
        total_schools = len(schools_data)
        processed_schools = 0
        failed_schools = 0

        for school_data in schools_data:
            try:
                self.prune_and_decompose_single_school_data(school_data)
                processed_schools += 1
            except Exception as e:
                failed_schools += 1
                logger.error(
                    f"📛 Error processing school, RSPO: {school_data.get('numerRspo', 'unknown')}, name: {school_data.get('nazwa', 'unknown')}, error: {e}"
                )
                session = self._ensure_session()
                session.rollback()

        logger.info(
            f"📊 Processing complete. Successfully processed: {processed_schools}/{total_schools} schools"
        )
        if failed_schools > 0:
            logger.warning(f"⚠️ Failed to process {failed_schools} schools")
