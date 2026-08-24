"""Chart extension points."""

from .schema import FileProfile


def build_charts(profile: FileProfile) -> list[dict]:
    """Return chart definitions for a file (reserved for a future release)."""

    return []

