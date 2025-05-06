import logging

from pydantic_core import ValidationError

from app.models.locations import Gmina, Miejscowosc, Powiat, Ulica, Wojewodztwo
from app.models.schools import (
    EtapEdukacji,
    EtapEdukacjiBase,
    KategoriaUczniow,
    KategoriaUczniowBase,
    KsztalcenieZawodowe,
    StatusPublicznoprawny,
    StatusPublicznoprawnyBase,
    Szkola,
    SzkolaEtapLink,  # noqa: F401
    TypSzkoly,
    TypSzkolyBase,
)
from data_import.api.db.excluded_fields import SchoolFieldExclusions
from data_import.api.models import SzkolaAPIResponse
from data_import.api.types import SchoolDict
from data_import.utils.db.session import DatabaseManagerBase

logger = logging.getLogger(__name__)


class Decomposer(DatabaseManagerBase):
    def __init__(self):
        super().__init__()
        self.voivodeships_cache: dict[str, Wojewodztwo] = {}
        self.counties_cache: dict[str, Powiat] = {}
        self.boroughs_cache: dict[str, Gmina] = {}
        self.localities_cache: dict[str, Miejscowosc] = {}
        self.streets_cache: dict[str, Ulica] = {}
        self.school_types_cache: dict[str, TypSzkoly] = {}
        self.statuses_cache: dict[str, StatusPublicznoprawny] = {}
        self.education_stages_cache: dict[str, EtapEdukacji] = {}
        self.student_categories_cache: dict[str, KategoriaUczniow] = {}
        self.vocational_trainings_cache: dict[str, KsztalcenieZawodowe] = {}

    def _get_or_create_entity[T: (Wojewodztwo, Powiat, Gmina, Miejscowosc, Ulica)](
        self,
        model_class: type[T],
        name: str,
        territorial_code: str,
        cache_dict: dict[str, T],
        **kwargs: Wojewodztwo | Powiat | Gmina,
    ) -> T:
        """
        Get or create an entity record (voivodeship, county, borough, or locality)

        Args:
            model_class: The model class to use (Wojewodztwo, Powiat, etc.)
            name: Name of the entity
            territorial_code: TERYT code of the entity
            cache_dict: Reference to the appropriate cache dictionary
            **kwargs: Additional keyword arguments like parent entities (wojewodztwo, powiat, etc.)

        Returns:
            The retrieved or created entity
        """
        if territorial_code in cache_dict:
            return cache_dict[territorial_code]

        entity = self._select_where(model_class, model_class.teryt == territorial_code)

        if not entity:
            entity = model_class(nazwa=name, teryt=territorial_code, **kwargs)  # pyright: ignore[reportArgumentType]

        cache_dict[territorial_code] = entity
        return entity

    def _get_or_create_school_type(self, school_type_base: TypSzkolyBase) -> TypSzkoly:
        """Get or create a school type record"""
        name = school_type_base.nazwa
        if name in self.school_types_cache:
            return self.school_types_cache[name]

        school_type = self._select_where(TypSzkoly, TypSzkoly.nazwa == name)

        if not school_type:
            school_type = TypSzkoly.model_validate(school_type_base)

        self.school_types_cache[name] = school_type
        return school_type

    def _get_or_create_status(
        self, status_base: StatusPublicznoprawnyBase
    ) -> StatusPublicznoprawny:
        """Get or create a public-legal status record"""
        name = status_base.nazwa
        if name in self.statuses_cache:
            return self.statuses_cache[name]

        school_status = self._select_where(
            StatusPublicznoprawny, StatusPublicznoprawny.nazwa == name
        )

        if not school_status:
            school_status = StatusPublicznoprawny.model_validate(status_base)

        self.statuses_cache[name] = school_status
        return school_status

    def _get_or_create_student_category(
        self, category_base: KategoriaUczniowBase
    ) -> KategoriaUczniow:
        """Get or create a student category record"""
        name = category_base.nazwa
        if name in self.student_categories_cache:
            return self.student_categories_cache[name]

        student_category = self._select_where(
            KategoriaUczniow, KategoriaUczniow.nazwa == name
        )

        if not student_category:
            student_category = KategoriaUczniow.model_validate(category_base)

        self.student_categories_cache[name] = student_category
        return student_category

    def _get_or_create_vocational_training(self, name: str) -> KsztalcenieZawodowe:
        """Get or create a vocational training record"""
        if name in self.vocational_trainings_cache:
            return self.vocational_trainings_cache[name]

        vocational_training = self._select_where(
            KsztalcenieZawodowe, KsztalcenieZawodowe.nazwa == name
        )

        if not vocational_training:
            vocational_training = KsztalcenieZawodowe(nazwa=name)

        self.vocational_trainings_cache[name] = vocational_training
        return vocational_training

    def _get_or_create_education_stage(
        self, education_stage_base: EtapEdukacjiBase
    ) -> EtapEdukacji:
        """Get or create an education stage record"""
        name = education_stage_base.nazwa
        if name in self.education_stages_cache:
            return self.education_stages_cache[name]

        education_stage = self._select_where(EtapEdukacji, EtapEdukacji.nazwa == name)

        if not education_stage:
            education_stage = EtapEdukacji.model_validate(education_stage_base)

        self.education_stages_cache[name] = education_stage
        return education_stage

    def _process_location_data(
        self, school_data: SzkolaAPIResponse
    ) -> tuple[Miejscowosc, Ulica | None]:
        """Process location data from school_data and return locality and street objects"""
        voivodeship = self._get_or_create_entity(
            model_class=Wojewodztwo,
            name=school_data.wojewodztwo,
            territorial_code=school_data.wojewodztwo_kod_TERYT,
            cache_dict=self.voivodeships_cache,
        )

        county = self._get_or_create_entity(
            model_class=Powiat,
            name=school_data.powiat,
            territorial_code=school_data.powiat_kod_TERYT,
            cache_dict=self.counties_cache,
            wojewodztwo=voivodeship,
        )

        borough = self._get_or_create_entity(
            model_class=Gmina,
            name=school_data.gmina,
            territorial_code=school_data.gmina_kod_TERYT,
            cache_dict=self.boroughs_cache,
            powiat=county,
        )

        locality = self._get_or_create_entity(
            model_class=Miejscowosc,
            name=school_data.miejscowosc,
            territorial_code=school_data.miejscowosc_kod_TERYT,
            cache_dict=self.localities_cache,
            gmina=borough,
        )

        street = None
        if school_data.ulica and school_data.ulica_kod_TERYT:
            street = self._get_or_create_entity(
                model_class=Ulica,
                name=school_data.ulica,
                territorial_code=school_data.ulica_kod_TERYT,
                cache_dict=self.streets_cache,
            )

        return locality, street

    def _process_school_other_information(
        self, school_data: SzkolaAPIResponse
    ) -> tuple[TypSzkoly, StatusPublicznoprawny, KategoriaUczniow]:
        """Process school type, status and student category data"""
        school_type = self._get_or_create_school_type(school_type_base=school_data.typ)
        status = self._get_or_create_status(
            status_base=school_data.status_publiczno_prawny
        )
        student_category = self._get_or_create_student_category(
            category_base=school_data.kategoria_uczniow
        )
        return school_type, status, student_category

    def _process_vocational_training_data(
        self, school_data: SzkolaAPIResponse
    ) -> list[KsztalcenieZawodowe]:
        """Process vocational training data"""
        if not school_data.ksztalcenie_zawodowe:
            return []

        vocational_trainings: list[KsztalcenieZawodowe] = []
        for value in school_data.ksztalcenie_zawodowe.values():
            training = self._get_or_create_vocational_training(name=value)
            vocational_trainings.append(training)

        return vocational_trainings

    def _process_education_stages(
        self, school_data: SzkolaAPIResponse
    ) -> list[EtapEdukacji]:
        """Process education stages data"""
        education_stages_list: list[EtapEdukacji] = []
        for education_stage_data in school_data.etapy_edukacji:
            stage = self._get_or_create_education_stage(
                education_stage_base=education_stage_data
            )
            education_stages_list.append(stage)
        return education_stages_list

    def _validate_required_school_data(
        self, school_data: SchoolDict
    ) -> SzkolaAPIResponse | None:
        """Validate that all required fields are present in the school data"""
        try:
            school_model = SzkolaAPIResponse.model_validate(school_data)
            return school_model
        except ValidationError as e:
            logger.error(f"❌ Invalid school data: {e}, School data: {school_data}")
            return None

    def _create_school_object(
        self,
        school_data: SzkolaAPIResponse,
        school_type: TypSzkoly,
        status: StatusPublicznoprawny,
        locality: Miejscowosc,
        street: Ulica | None,
        education_stages: list[EtapEdukacji],
        vocational_trainings: list[KsztalcenieZawodowe],
        student_category: KategoriaUczniow,
    ) -> Szkola:
        """Create a new school object from validated data"""
        geolocation = school_data.geolokalizacja

        api_school_data_dict = school_data.model_dump()
        # remove specific columns to prevent multiple values for the same field
        for column in SchoolFieldExclusions.ALL:
            api_school_data_dict.pop(column)

        # all other fields from SzkolaAPIResponse that are not used in Szkola are removed by pydantic
        new_school = Szkola(
            **api_school_data_dict,  # pyright: ignore[reportAny]
            geolokalizacja_latitude=geolocation.latitude,
            geolokalizacja_longitude=geolocation.longitude,
            typ=school_type,
            status_publicznoprawny=status,  # we haven't removed status_publicznoprawny from SzkolaAPIResponse because from the API we actually have status_publiczno_prawny which is incorrect form
            miejscowosc=locality,
            ulica=street,
            etapy_edukacji=education_stages,
            ksztalcenie_zawodowe=vocational_trainings,
            kategoria_uczniow=student_category,
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
            locality, street = self._process_location_data(school)

            # Process school type and status data
            school_type, school_status, student_category = (
                self._process_school_other_information(school)
            )

            # Process vocational training data
            vocational_trainings_list = self._process_vocational_training_data(school)

            # Process education stages data
            education_stages_list = self._process_education_stages(school)

            # Create a new school object
            new_school_object = self._create_school_object(
                school_data=school,
                school_type=school_type,
                status=school_status,
                locality=locality,
                street=street,
                education_stages=education_stages_list,
                vocational_trainings=vocational_trainings_list,
                student_category=student_category,
            )

            session.add(new_school_object)
            session.commit()
            session.refresh(new_school_object)

            logger.info(
                f"💾 Added school: {new_school_object.nazwa} (RSPO: {new_school_object.numer_rspo})"
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
