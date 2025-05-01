from types import TracebackType
from typing import Self

from sqlalchemy import Engine
from sqlmodel import Session

from app.core.database import engine


class SessionManagerBase:
    """Base class providing session management functionality"""

    engine: Engine
    session: Session | None

    def __init__(self):
        self.engine = engine
        self.session = None

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
