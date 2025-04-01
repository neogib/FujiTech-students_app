import logging
from types import TracebackType

from sqlalchemy import Engine
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
from .types.constants import LocationKeys, NestedKeys, SchoolKeys
from .types.school_data import SchoolDataDict

logger = logging.getLogger(__name__)


class DatabaseDecomposer:
    def __init__(self):
        self.engine: Engine = engine
        self.session: Session | None = None
        self.wojewodztwa_cache: dict[str, Wojewodztwa] = {}
        self.powiaty_cache: dict[str, Powiaty] = {}
        self.gminy_cache: dict[str, Gminy] = {}
        self.miejscowosci_cache: dict[str, Miejscowosci] = {}
        self.ulice_cache: dict[str, Ulice | None] = {}
        self.typy_szkol_cache: dict[str, TypySzkol] = {}
        self.statusy_cache: dict[str, StatusPublicznoprawny] = {}
        self.etapy_edukacji_cache: dict[str, EtapyEdukacji] = {}

    def __enter__(self) -> "DatabaseDecomposer":
        # Create the session when entering the context
        self.session = Session(self.engine)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        # Close the session when exiting the context
        self.close()

    def close(self) -> None:
        """Manual close method for when not using as context manager"""
        if self.session:
            self.session.close()
            self.session = None

    def _ensure_session(self) -> Session:
        """Ensure we have an active session and return it"""
        if self.session is None:
            self.session = Session(self.engine)
        return self.session

    def _log_missing_required_key(
        self, school_data: SchoolDataDict, e: Exception, required_key: str
    ) -> None:
        """Log an error when a required key is missing"""
        logger.error(
            f"""❌ Missing required {required_key} data for school:
                - RSPO: {school_data.get(SchoolKeys.RSPO, "unknown")},
                - name: {school_data.get(SchoolKeys.NAME, "unknown")}, 
                - error: {e}"""
        )
        self._ensure_session().rollback()

    def _select_where(self, model, condition):
        """Generic method to select a record based on a condition"""
        session = self._ensure_session()
        return session.exec(select(model).where(condition)).first()

    def _get_or_create_wojewodztwo(self, nazwa: str, teryt: str) -> Wojewodztwa:
        """Get or create a voivodeship record"""
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
        """Get or create a county record"""
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.powiaty_cache:
            return self.powiaty_cache[cache_key]

        powiat = self._select_where(Powiaty, Powiaty.teryt == teryt)

        if not powiat:
            powiat = Powiaty(nazwa=nazwa, teryt=teryt, wojewodztwo=wojewodztwo)

        self.powiaty_cache[cache_key] = powiat
        return powiat

    def _get_or_create_gmina(self, nazwa: str, teryt: str, powiat: Powiaty) -> Gminy:
        """Get or create a borough record"""
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
        """Get or create a city record"""
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.miejscowosci_cache:
            return self.miejscowosci_cache[cache_key]

        miejscowosc = self._select_where(Miejscowosci, Miejscowosci.teryt == teryt)

        if not miejscowosc:
            miejscowosc = Miejscowosci(nazwa=nazwa, teryt=teryt, gmina=gmina)

        self.miejscowosci_cache[cache_key] = miejscowosc
        return miejscowosc

    def _get_or_create_ulica(
        self, nazwa: str | None, teryt: str | None
    ) -> Ulice | None:
        """Get or create a street record if both name and teryt are provided"""
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
        """Get or create a school type record"""
        if nazwa in self.typy_szkol_cache:
            return self.typy_szkol_cache[nazwa]

        typ_szkoly = self._select_where(TypySzkol, TypySzkol.nazwa == nazwa)

        if not typ_szkoly:
            typ_szkoly = TypySzkol(nazwa=nazwa)

        self.typy_szkol_cache[nazwa] = typ_szkoly
        return typ_szkoly

    def _get_or_create_status(self, nazwa: str) -> StatusPublicznoprawny:
        """Get or create a public-legal status record"""
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
        """Get or create an education stage record"""
        if nazwa in self.etapy_edukacji_cache:
            return self.etapy_edukacji_cache[nazwa]

        etap = self._select_where(EtapyEdukacji, EtapyEdukacji.nazwa == nazwa)

        if not etap:
            etap = EtapyEdukacji(nazwa=nazwa)

        self.etapy_edukacji_cache[nazwa] = etap
        return etap

    def _process_location_data(
        self, school_data: SchoolDataDict
    ) -> tuple[Miejscowosci, Ulice | None]:
        """Process location data from school_data and return miejscowosc and ulica objects"""
        try:
            wojewodztwo = self._get_or_create_wojewodztwo(
                nazwa=school_data[LocationKeys.VOIVODESHIP],
                teryt=school_data[LocationKeys.VOIVODESHIP_TERYT],
            )

            powiat = self._get_or_create_powiat(
                nazwa=school_data[LocationKeys.COUNTY],
                teryt=school_data[LocationKeys.COUNTY_TERYT],
                wojewodztwo=wojewodztwo,
            )

            gmina = self._get_or_create_gmina(
                nazwa=school_data[LocationKeys.COMMUNE],
                teryt=school_data[LocationKeys.COMMUNE_TERYT],
                powiat=powiat,
            )

            miejscowosc = self._get_or_create_miejscowosc(
                nazwa=school_data[LocationKeys.CITY],
                teryt=school_data[LocationKeys.CITY_TERYT],
                gmina=gmina,
            )

            ulica = None
            if (
                LocationKeys.STREET in school_data
                and LocationKeys.STREET_TERYT in school_data
            ):
                ulica = self._get_or_create_ulica(
                    nazwa=school_data.get(LocationKeys.STREET),
                    teryt=school_data.get(LocationKeys.STREET_TERYT),
                )

            return miejscowosc, ulica
        except KeyError as e:
            raise ValueError(f"Missing location data: {e}")

    def _process_school_type_data(
        self, school_data: SchoolDataDict
    ) -> tuple[TypySzkol, StatusPublicznoprawny]:
        """Process school type and status data"""
        try:
            typ = self._get_or_create_typ_szkoly(
                nazwa=school_data[SchoolKeys.TYPE][NestedKeys.TYPE_NAME]
            )
            status = self._get_or_create_status(
                nazwa=school_data[SchoolKeys.STATUS][NestedKeys.STATUS_NAME]
            )
            return typ, status
        except KeyError as e:
            raise ValueError(f"Missing school type or status data: {e}")

    def _process_education_stages(
        self, school_data: SchoolDataDict
    ) -> list[EtapyEdukacji]:
        """Process education stages data"""
        try:
            etapy: list[EtapyEdukacji] = []
            for etap_data in school_data[SchoolKeys.EDUCATION_STAGES]:
                etap = self._get_or_create_etap_edukacji(
                    nazwa=etap_data[NestedKeys.EDUCATION_STAGE_NAME]
                )
                etapy.append(etap)
            return etapy
        except KeyError as e:
            raise ValueError(f"Invalid education stage data: {e}")

    def _validate_required_school_data(self, school_data: SchoolDataDict) -> bool:
        """Validate that all required fields are present in the school data"""
        required_fields = [
            SchoolKeys.RSPO,
            SchoolKeys.REGON,
            SchoolKeys.NAME,
            SchoolKeys.POSTAL_CODE,
            SchoolKeys.GEOLOCATION,
        ]

        for field in required_fields:
            if field not in school_data:
                logger.error(
                    f"❌ Missing required field {field} for school: {school_data.get(SchoolKeys.NAME, 'unknown')}"
                )
                return False

        # Check nested required fields
        geolocation = school_data[SchoolKeys.GEOLOCATION]
        if (
            NestedKeys.GEOLOCATION_LATITUDE not in geolocation
            or NestedKeys.GEOLOCATION_LONGITUDE not in geolocation
        ):
            logger.error(
                f"❌ Invalid geolocation data for school: {school_data.get(SchoolKeys.NAME, 'unknown')}"
            )
            return False

        return True

    def _create_school_object(
        self,
        school_data: SchoolDataDict,
        typ: TypySzkol,
        status: StatusPublicznoprawny,
        miejscowosc: Miejscowosci,
        ulica: Ulice | None,
        etapy: list[EtapyEdukacji],
    ) -> Szkoly:
        """Create a new school object from validated data"""
        try:
            geolokalizacja = school_data[SchoolKeys.GEOLOCATION]

            # Create new school with proper None handling for optional fields
            new_school = Szkoly(
                numer_rspo=school_data[SchoolKeys.RSPO],
                nip=school_data.get(SchoolKeys.NIP) or None,
                regon=school_data[SchoolKeys.REGON],
                liczba_uczniow=school_data.get(
                    SchoolKeys.STUDENTS_COUNT
                ),  # No "or None" to allow 0 value
                nazwa=school_data[SchoolKeys.NAME],
                dyrektor_imie=school_data.get(SchoolKeys.DIRECTOR_FIRST_NAME) or None,
                dyrektor_nazwisko=school_data.get(SchoolKeys.DIRECTOR_LAST_NAME)
                or None,
                geolokalizacja_latitude=geolokalizacja[NestedKeys.GEOLOCATION_LATITUDE],
                geolokalizacja_longitude=geolokalizacja[
                    NestedKeys.GEOLOCATION_LONGITUDE
                ],
                kod_pocztowy=school_data[SchoolKeys.POSTAL_CODE],
                numer_budynku=school_data.get(SchoolKeys.BUILDING_NUMBER) or None,
                numer_lokalu=school_data.get(SchoolKeys.APARTMENT_NUMBER) or None,
                telefon=school_data.get(SchoolKeys.PHONE) or None,
                email=school_data.get(SchoolKeys.EMAIL) or None,
                strona_internetowa=school_data.get(SchoolKeys.WEBSITE) or None,
                # relationships
                typ=typ,
                status=status,
                miejscowosc=miejscowosc,
                ulica=ulica,
                etapy=etapy,
            )

            return new_school
        except KeyError as e:
            raise ValueError(f"Missing required school data: {e}")

    def prune_and_decompose_single_school_data(
        self, school_data: SchoolDataDict
    ) -> None:
        """Process a single school's data and save to database"""
        session = self._ensure_session()

        # First, validate the minimum required fields
        if not self._validate_required_school_data(school_data):
            session.rollback()
            return

        try:
            # Check if school already exists
            existing_school = self._select_where(
                Szkoly, Szkoly.numer_rspo == school_data[SchoolKeys.RSPO]
            )

            if existing_school:
                logger.info(
                    f"🔙 School with RSPO {school_data[SchoolKeys.RSPO]} already exists. Skipping."
                )
                return

            try:
                # Process location data
                miejscowosc, ulica = self._process_location_data(school_data)

                # Process school type and status
                typ, status = self._process_school_type_data(school_data)

                # Process education stages
                etapy = self._process_education_stages(school_data)

                # Create and save new school
                new_school = self._create_school_object(
                    school_data, typ, status, miejscowosc, ulica, etapy
                )

                session.add(new_school)
                session.commit()
                session.refresh(new_school)

                logger.info(
                    f"💾 Added school: {new_school.nazwa} (RSPO: {new_school.numer_rspo})"
                )

            except ValueError as e:
                self._log_missing_required_key(school_data, e, str(e))
                return

        except Exception as e:
            logger.error(
                f"❌ Unexpected error processing school {school_data.get(SchoolKeys.RSPO, 'unknown')}: {e}"
            )
            session.rollback()
            return

    def prune_and_decompose_schools(self, schools_data: list[SchoolDataDict]) -> None:
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
                    f"📛 Error processing school, RSPO: {school_data.get(SchoolKeys.RSPO, 'unknown')}, name: {school_data.get(SchoolKeys.NAME, 'unknown')}, error: {e}"
                )
                session = self._ensure_session()
                session.rollback()

        logger.info(
            f"📊 Processing complete. Successfully processed: {processed_schools}/{total_schools} schools"
        )
        if failed_schools > 0:
            logger.warning(f"⚠️ Failed to process {failed_schools} schools")
