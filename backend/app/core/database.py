from sqlmodel import Session, SQLModel, create_engine

from .config import settings

# DATABASE_URI is of type PostgresDsn, that's why we need get_connection_string method
engine = create_engine(settings.get_connection_string(), echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
