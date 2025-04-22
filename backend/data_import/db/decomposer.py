import logging
from types import TracebackType
from typing import Self

from pydantic_core import ValidationError
from sqlalchemy import Engine
from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import Session, SQLModel, select

from ...app.core.database import engine
from ...app.models.locations import Gmina, Miejscowosc, Powiat, Ulica, Wojewodztwo
from ...app.models.schools import (
    EtapEdukacji,
    EtapEdukacjiBase,
    StatusPublicznoprawny,
    StatusPublicznoprawnyBase,
    Szkola,
    SzkolaEtapLink,  # noqa: F401
    TypSzkoly,
    TypSzkolyBase,
)
from ..api.models import SzkolaAPIResponse
from ..api.types import SchoolDict
from .excluded_fields import SchoolFieldExclusions

logger = logging.getLogger(__name__)


class DatabaseDecomposer:
    def __init__(self):
        self.engine: Engine = engine
        self.session: Session | None = None
        self.wojewodztwa_cache: dict[str, Wojewodztwo] = {}
        self.powiaty_cache: dict[str, Powiat] = {}
        self.gminy_cache: dict[str, Gmina] = {}
        self.miejscowosci_cache: dict[str, Miejscowosc] = {}
        self.ulice_cache: dict[str, Ulica | None] = {}
        self.typy_cache: dict[str, TypSzkoly] = {}
        self.statusy_cache: dict[str, StatusPublicznoprawny] = {}
        self.etapy_edukacji_cache: dict[str, EtapEdukacji] = {}

    def __enter__(self) -> Self:
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

    def _select_where[T: SQLModel](
        self, model: type[T], condition: BinaryExpression[bool] | bool
    ) -> T | None:
        """Generic method to select a record based on a condition"""
        session = self._ensure_session()
        return session.exec(select(model).where(condition)).first()

    def _get_or_create_wojewodztwo(self, nazwa: str, teryt: str) -> Wojewodztwo:
        """Get or create a voivodeship record"""
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.wojewodztwa_cache:
            return self.wojewodztwa_cache[cache_key]

        wojewodztwo = self._select_where(Wojewodztwo, Wojewodztwo.teryt == teryt)

        if not wojewodztwo:
            wojewodztwo = Wojewodztwo(nazwa=nazwa, teryt=teryt)

        self.wojewodztwa_cache[cache_key] = wojewodztwo
        return wojewodztwo

    def _get_or_create_powiat(
        self, nazwa: str, teryt: str, wojewodztwo: Wojewodztwo
    ) -> Powiat:
        """Get or create a county record"""
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.powiaty_cache:
            return self.powiaty_cache[cache_key]

        powiat = self._select_where(Powiat, Powiat.teryt == teryt)

        if not powiat:
            powiat = Powiat(nazwa=nazwa, teryt=teryt, wojewodztwo=wojewodztwo)

        self.powiaty_cache[cache_key] = powiat
        return powiat

    def _get_or_create_gmina(self, nazwa: str, teryt: str, powiat: Powiat) -> Gmina:
        """Get or create a borough record"""
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.gminy_cache:
            return self.gminy_cache[cache_key]

        gmina = self._select_where(Gmina, Gmina.teryt == teryt)

        if not gmina:
            gmina = Gmina(nazwa=nazwa, teryt=teryt, powiat=powiat)

        self.gminy_cache[cache_key] = gmina
        return gmina

    def _get_or_create_miejscowosc(
        self, nazwa: str, teryt: str, gmina: Gmina
    ) -> Miejscowosc:
        """Get or create a city record"""
        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.miejscowosci_cache:
            return self.miejscowosci_cache[cache_key]

        miejscowosc = self._select_where(Miejscowosc, Miejscowosc.teryt == teryt)

        if not miejscowosc:
            miejscowosc = Miejscowosc(nazwa=nazwa, teryt=teryt, gmina=gmina)

        self.miejscowosci_cache[cache_key] = miejscowosc
        return miejscowosc

    def _get_or_create_ulica(
        self, nazwa: str | None, teryt: str | None
    ) -> Ulica | None:
        """Get or create a street record if both name and teryt are provided"""
        if not nazwa or not teryt:
            return None

        cache_key = f"{nazwa}_{teryt}"
        if cache_key in self.ulice_cache:
            return self.ulice_cache[cache_key]

        ulica = self._select_where(Ulica, Ulica.teryt == teryt)

        if not ulica:
            ulica = Ulica(nazwa=nazwa, teryt=teryt)

        self.ulice_cache[cache_key] = ulica
        return ulica

    def _get_or_create_typ_szkoly(self, typ: TypSzkolyBase) -> TypSzkoly:
        """Get or create a school type record"""
        nazwa = typ.nazwa
        if nazwa in self.typy_cache:
            return self.typy_cache[nazwa]

        typ_szkoly = self._select_where(TypSzkoly, TypSzkoly.nazwa == nazwa)

        if not typ_szkoly:
            typ_szkoly = TypSzkoly.model_validate(typ)

        self.typy_cache[nazwa] = typ_szkoly
        return typ_szkoly

    def _get_or_create_status(
        self, status: StatusPublicznoprawnyBase
    ) -> StatusPublicznoprawny:
        """Get or create a public-legal status record"""
        nazwa = status.nazwa
        if nazwa in self.statusy_cache:
            return self.statusy_cache[nazwa]

        status_szkoly = self._select_where(
            StatusPublicznoprawny, StatusPublicznoprawny.nazwa == nazwa
        )

        if not status_szkoly:
            status_szkoly = StatusPublicznoprawny.model_validate(status)

        self.statusy_cache[nazwa] = status_szkoly
        return status_szkoly

    def _get_or_create_etap_edukacji(self, etap_data: EtapEdukacjiBase) -> EtapEdukacji:
        """Get or create an education stage record"""
        nazwa = etap_data.nazwa
        if nazwa in self.etapy_edukacji_cache:
            return self.etapy_edukacji_cache[nazwa]

        etap = self._select_where(EtapEdukacji, EtapEdukacji.nazwa == nazwa)

        if not etap:
            etap = EtapEdukacji.model_validate(etap_data)

        self.etapy_edukacji_cache[nazwa] = etap
        return etap

    def _process_location_data(
        self, school_data: SzkolaAPIResponse
    ) -> tuple[Miejscowosc, Ulica | None]:
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
        self, school_data: SzkolaAPIResponse
    ) -> tuple[TypSzkoly, StatusPublicznoprawny]:
        """Process school type and status data"""
        typ = self._get_or_create_typ_szkoly(typ=school_data.typ)
        status = self._get_or_create_status(status=school_data.status_publiczno_prawny)
        return typ, status

    def _process_education_stages(
        self, school_data: SzkolaAPIResponse
    ) -> list[EtapEdukacji]:
        """Process education stages data"""
        etapy: list[EtapEdukacji] = []
        for etap_data in school_data.etapy_edukacji:
            etap = self._get_or_create_etap_edukacji(etap_data=etap_data)
            etapy.append(etap)
        return etapy

    def _validate_required_school_data(
        self, school_data: SchoolDict
    ) -> SzkolaAPIResponse | None:
        """Validate that all required fields are present in the school data"""
        try:
            school = SzkolaAPIResponse.model_validate(school_data)
            return school
        except ValidationError as e:
            logger.error(f"❌ Invalid school data: {e}, School data: {school_data}")
            return None

    def _create_school_object(
        self,
        school_data: SzkolaAPIResponse,
        typ: TypSzkoly,
        status: StatusPublicznoprawny,
        miejscowosc: Miejscowosc,
        ulica: Ulica | None,
        etapy: list[EtapEdukacji],
    ) -> Szkola:
        """Create a new school object from validated data"""
        geolokalizacja = school_data.geolokalizacja

        api_school_data = school_data.model_dump()
        # remove specific columns to prevent multiple values for the same field
        for column in SchoolFieldExclusions.ALL:
            api_school_data.pop(column)

        # all other fields from SzkolaAPIResponse that are not used in Szkola are removed by pydantic
        new_school = Szkola(
            **api_school_data,  # pyright: ignore[reportAny]
            geolokalizacja_latitude=geolokalizacja.latitude,
            geolokalizacja_longitude=geolokalizacja.longitude,
            typ=typ,
            status_publicznoprawny=status,  # we haven't removed status_publicznoprawny from SzkolaAPIResponse because from the API we actually have status_publiczno_prawny which is incorrect form
            miejscowosc=miejscowosc,
            ulica=ulica,
            etapy_edukacji=etapy,
        )

        return new_school

    def prune_and_decompose_single_school_data(self, school_data: SchoolDict) -> None:
        """Process a single school's data and save to database"""
        session = self._ensure_session()

        # First, validate the required fields using the power of Pydantic
        school = self._validate_required_school_data(school_data)
        if not school:
            session.rollback()
            return

        try:
            # Check if school already exists
            existing_school = self._select_where(
                Szkola, Szkola.numer_rspo == school.numer_rspo
            )

            if existing_school:
                logger.info(
                    f"🔙 School with RSPO {school.numer_rspo} already exists. Skipping."
                )
                return

            # Process location data
            miejscowosc, ulica = self._process_location_data(school)

            # Process school type and status
            typ, status = self._process_school_type_data(school)

            # Process education stages
            etapy = self._process_education_stages(school)

            # Create and save new school
            new_school = self._create_school_object(
                school, typ, status, miejscowosc, ulica, etapy
            )

            session.add(new_school)
            session.commit()
            session.refresh(new_school)

            logger.info(
                f"💾 Added school: {new_school.nazwa} (RSPO: {new_school.numer_rspo})"
            )

        except Exception as e:
            logger.error(
                f"❌ Unexpected error processing school {school.numer_rspo}: {e}"
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
