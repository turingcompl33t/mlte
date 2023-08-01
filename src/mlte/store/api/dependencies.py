"""
mlte/store/frontend/dependencies.py

This file defines common dependencies that are used by API functions.
In practice, this ensures that the backend is initialized prior to
attempting to service any incoming requests.

Originally, I used FastAPI dependency injection to manage dependencies,
but it became so much harder to manage the fact that initialization was
occurring at import time rather than at invocation time that I removed
this in favor of slightly more brittle but eminently more workable
solution that involves manual context management with a global state object.
"""

from typing import Generator
from mlte.store.state import state
from mlte.store.backend import SessionHandle
from contextlib import contextmanager


@contextmanager
def get_handle() -> Generator[SessionHandle, None, None]:
    """
    Get a handle to backend session.
    :return: The handle
    """
    try:
        handle = state.engine.handle()
        yield handle
    finally:
        handle.close()
