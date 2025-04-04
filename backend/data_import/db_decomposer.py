import logging
from types import TracebackType

from pydantic_core import ValidationError
from sqlalchemy import Engine
from sqlmodel import Session, select

from .types import SchoolDict

from ..app.core.database import engine
from ..app.models.locations import Gminy, Miejscowosci, Powiaty, Ulice, Wojewodztwa
from ..app.models.schools import (
    EtapyEdukacji,
    EtapyEdukacjiBase,
    StatusPublicznoprawny,
    StatusPublicznoprawnyBase,
    Szkoly,
    SzkolyAPIResponse,
    SzkolyEtapyLink,  # noqa: F401
    TypySzkol,
    TypySzkolBase,
)

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
        self.statusy_szkol_cache: dict[str, StatusPublicznoprawny] = {}
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
        self, school_data: SzkolyAPIResponse, e: Exception, required_key: str
    ) -> None:
        """Log an error when a required key is missing"""
        logger.error(
            f"""❌ Missing required {required_key} data for school:
                - RSPO: {school_data.numer_rspo},
                - name: {school_data.nazwa}, 
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

    def _get_or_create_typ_szkoly(self, typ: TypySzkolBase) -> TypySzkol:
        """Get or create a school type record"""
        nazwa = typ.nazwa
        if nazwa in self.typy_szkol_cache:
            return self.typy_szkol_cache[nazwa]

        typ_szkoly = self._select_where(TypySzkol, TypySzkol.nazwa == nazwa)

        if not typ_szkoly:
            typ_szkoly = TypySzkol.model_validate(typ)

        self.typy_szkol_cache[nazwa] = typ_szkoly
        return typ_szkoly

    def _get_or_create_status(
        self, status: StatusPublicznoprawnyBase
    ) -> StatusPublicznoprawny:
        """Get or create a public-legal status record"""
        nazwa = status.nazwa
        if nazwa in self.statusy_szkol_cache:
            return self.statusy_szkol_cache[nazwa]

        status_szkoly = self._select_where(
            StatusPublicznoprawny, StatusPublicznoprawny.nazwa == nazwa
        )

        if not status_szkoly:
            status_szkoly = StatusPublicznoprawny.model_validate(status)

        self.statusy_szkol_cache[nazwa] = status_szkoly
        return status_szkoly

    def _get_or_create_etap_edukacji(
        self, etap_data: EtapyEdukacjiBase
    ) -> EtapyEdukacji:
        """Get or create an education stage record"""
        nazwa = etap_data.nazwa
        if nazwa in self.etapy_edukacji_cache:
            return self.etapy_edukacji_cache[nazwa]

        etap = self._select_where(EtapyEdukacji, EtapyEdukacji.nazwa == nazwa)

        if not etap:
            etap = EtapyEdukacji.model_validate(etap_data)

        self.etapy_edukacji_cache[nazwa] = etap
        return etap

    def _process_location_data(
        self, school_data: SzkolyAPIResponse
    ) -> tuple[Miejscowosci, Ulice | None]:
        """Process location data from school_data and return miejscowosc and ulica objects"""
        wojewodztwo = self._get_or_create_wojewodztwo(
            nazwa=school_data.wojewodztwo,
            teryt=school_data.wojewodztwo_kod_TERYT,
        )

        powiat = self._get_or_create_powiat(
            nazwa=school_data.powiat,
            teryt=school_data.powiat_kod_TERYT,
            wojewodztwo=wojewodztwo,
        )

        gmina = self._get_or_create_gmina(
            nazwa=school_data.gmina,
            teryt=school_data.gmina_kod_TERYT,
            powiat=powiat,
        )

        miejscowosc = self._get_or_create_miejscowosc(
            nazwa=school_data.miejscowosc,
            teryt=school_data.miejscowosc_kod_TERYT,
            gmina=gmina,
        )

        ulica = None
        if school_data.ulica and school_data.ulica_kod_TERYT:
            ulica = self._get_or_create_ulica(
                nazwa=school_data.ulica,
                teryt=school_data.ulica_kod_TERYT,
            )

        return miejscowosc, ulica

    def _process_school_type_data(
        self, school_data: SzkolyAPIResponse
    ) -> tuple[TypySzkol, StatusPublicznoprawny]:
        """Process school type and status data"""
        typ = self._get_or_create_typ_szkoly(typ=school_data.typ)
        status = self._get_or_create_status(status=school_data.status_publiczno_prawny)
        return typ, status

    def _process_education_stages(
        self, school_data: SzkolyAPIResponse
    ) -> list[EtapyEdukacji]:
        """Process education stages data"""
        etapy: list[EtapyEdukacji] = []
        for etap_data in school_data.etapy_edukacji:
            etap = self._get_or_create_etap_edukacji(etap_data=etap_data)
            etapy.append(etap)
        return etapy

    def _validate_required_school_data(
        self, school_data: SchoolDict
    ) -> SzkolyAPIResponse | None:
        """Validate that all required fields are present in the school data"""
        try:
            school = SzkolyAPIResponse.model_validate(school_data)
            return school
        except ValidationError as e:
            logger.error(f"❌ Invalid school data: {e}")
            return None

    #     required_fields = [
    #         SchoolKeys.RSPO,
    #         SchoolKeys.REGON,
    #         SchoolKeys.NAME,
    #         SchoolKeys.POSTAL_CODE,
    #         SchoolKeys.GEOLOCATION,
    #     ]
    #
    #     for field in required_fields:
    #         if field not in school_data:
    #             logger.error(
    #                 f"❌ Missing required field {field} for school: {school_data.get(SchoolKeys.NAME, 'unknown')}"
    #             )
    #             return False
    #
    #     # Check nested required fields
    #     geolocation = school_data[SchoolKeys.GEOLOCATION]
    #     if (
    #         NestedKeys.GEOLOCATION_LATITUDE not in geolocation
    #         or NestedKeys.GEOLOCATION_LONGITUDE not in geolocation
    #     ):
    #         logger.error(
    #             f"❌ Invalid geolocation data for school: {school_data.get(SchoolKeys.NAME, 'unknown')}"
    #         )
    #         return False
    #
    #     return True

    def _create_school_object(
        self,
        school_data: SzkolyAPIResponse,
        typ: TypySzkol,
        status: StatusPublicznoprawny,
        miejscowosc: Miejscowosci,
        ulica: Ulice | None,
        etapy: list[EtapyEdukacji],
    ) -> Szkoly:
        """Create a new school object from validated data"""
        geolokalizacja = school_data.geolokalizacja

        new_school = Szkoly(
            **school_data.model_dump(),
            geolokalizacja_latitude=geolokalizacja.latitude,
            geolokalizacja_longitude=geolokalizacja.longitude,
            typ=typ,
            status=status,
            miejscowosc=miejscowosc,
            ulica=ulica,
            etapy=etapy,
        )

        return new_school

    def prune_and_decompose_single_school_data(self, school_data: SchoolDict) -> None:
        """Process a single school's data and save to database"""
        session = self._ensure_session()

        # First, validate the required fields using the power of Pydantic
        schools = self._validate_required_school_data(school_data)
        if not schools:
            session.rollback()
            return

        try:
            # Check if school already exists
            existing_school = self._select_where(
                Szkoly, Szkoly.numer_rspo == schools.numer_rspo
            )

            if existing_school:
                logger.info(
                    f"🔙 School with RSPO {schools.numer_rspo} already exists. Skipping."
                )
                return

            # Process location data
            miejscowosc, ulica = self._process_location_data(schools)

            # Process school type and status
            typ, status = self._process_school_type_data(schools)

            # Process education stages
            etapy = self._process_education_stages(schools)

            # Create and save new school
            new_school = self._create_school_object(
                schools, typ, status, miejscowosc, ulica, etapy
            )

            session.add(new_school)
            session.commit()
            session.refresh(new_school)

            logger.info(
                f"💾 Added school: {new_school.nazwa} (RSPO: {new_school.numer_rspo})"
            )

        except Exception as e:
            logger.error(
                f"❌ Unexpected error processing school {schools.numer_rspo}: {e}"
            )
            session.rollback()
            return

    def prune_and_decompose_schools(self, schools_data: list[SchoolDict]) -> None:
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
                    f"📛 Error processing school: {school_data.get('numerRspo', 'unknown')}: {e}"
                )
                session = self._ensure_session()
                session.rollback()

        logger.info(
            f"📊 Processing complete. Successfully processed: {processed_schools}/{total_schools} schools"
        )
        if failed_schools > 0:
            logger.warning(f"⚠️ Failed to process {failed_schools} schools")
