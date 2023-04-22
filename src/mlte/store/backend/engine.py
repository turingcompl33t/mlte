"""
store/backend/engine.py

Backend engine creation. This is the first
step in the backend initialization lifecycle.
"""

from mlte.store.backend import BackendEngine, BackendURI, BackendType
from mlte.store.backend.fs import FilesystemBackendEngine
from mlte.store.core.config import settings


def _parse_uri(uri: str) -> BackendURI:
    """
    Parse the URI for a backend store.
    :param uri: The URI for the backend store
    :type uri: str
    :return: The parsed BackendStoreURI
    :rtype: BackendStoreURI
    """
    return BackendURI.from_string(uri)


def create_engine() -> BackendEngine:
    """
    Create the
    """
    parsed_uri = _parse_uri(settings.BACKEND_URI)
    if parsed_uri.type == BackendType.FS:
        return FilesystemBackendEngine.create(parsed_uri)
    raise RuntimeError(f"Unknown URI type: {parsed_uri}.")


# The global backend engine
g_engine: BackendEngine = create_engine()
