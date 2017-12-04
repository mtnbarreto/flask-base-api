# project/utils/helpers.py
from contextlib import contextmanager
from project.api.common.exceptions import ServerErrorException

@contextmanager
def session_scope(session):
    """Provide a transactional scope around a series of operations."""
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise ServerErrorException()
