"""Path traversal guard — opt-in via PETP_PATH_ALLOW_ROOTS env var.

Phase 2 P1-2 lays the foundation for closing CWE-22 in file IO processors
(READ_*, WRITE_*, OPEN_FILE, FILE_DELETE, ZIP, UNZIP, FIND_FILES, ...). When
PETP_PATH_ALLOW_ROOTS is unset (default), validate_path() returns the
canonicalized path unchanged — preserving every existing yaml that uses
absolute paths outside the project tree.

When operators set PETP_PATH_ALLOW_ROOTS=root1:root2:..., validate_path()
canonicalizes the input and rejects any path that does not resolve under one
of the listed roots. This is the recommended posture for NAS/Docker
deployments where untrusted yaml may reach the runner.

Usage in a processor:

    from utils.SafePaths import validate_path
    file_path = validate_path(self.expression2str(self.get_param('file_path')))
    with open(file_path, 'r') as f:
        ...

The default-off design means this module can be added incrementally without
breaking any existing deployment. Operators opt in when they need it.
"""
import logging
import os
from pathlib import Path
from typing import List, Optional

_logger = logging.getLogger(__name__)

_ENV_KEY = 'PETP_PATH_ALLOW_ROOTS'
_resolved_roots: Optional[List[Path]] = None


def _resolve_roots() -> List[Path]:
    """Lazy-parse PETP_PATH_ALLOW_ROOTS once per process. Empty list = guard off."""
    global _resolved_roots
    if _resolved_roots is not None:
        return _resolved_roots

    raw = os.environ.get(_ENV_KEY, '').strip()
    if not raw:
        _resolved_roots = []
        return _resolved_roots

    sep = ';' if os.name == 'nt' else ':'
    roots: List[Path] = []
    for entry in raw.split(sep):
        entry = entry.strip()
        if not entry:
            continue
        try:
            roots.append(Path(entry).expanduser().resolve())
        except (OSError, RuntimeError) as exc:
            _logger.warning('PETP_PATH_ALLOW_ROOTS: ignoring invalid root %r (%s)', entry, exc)

    _resolved_roots = roots
    if roots:
        _logger.info('PETP_PATH_ALLOW_ROOTS active: %s', [str(p) for p in roots])
    return _resolved_roots


def is_guard_active() -> bool:
    return bool(_resolve_roots())


def validate_path(file_path: str) -> str:
    """Canonicalize and (if guard active) enforce path is under an allowed root.

    Returns the canonical absolute path on success. Raises PermissionError when
    PETP_PATH_ALLOW_ROOTS is set and the path falls outside every allowed root.
    Raises ValueError if file_path is empty.

    When PETP_PATH_ALLOW_ROOTS is unset, the path is canonicalized (resolves
    symlinks and `..`) but never rejected — preserves existing behavior.
    """
    if not file_path:
        raise ValueError('file_path must not be empty')

    try:
        canonical = Path(file_path).expanduser().resolve()
    except (OSError, RuntimeError) as exc:
        raise ValueError(f'cannot canonicalize path {file_path!r}: {exc}') from exc

    roots = _resolve_roots()
    if not roots:
        return str(canonical)

    for root in roots:
        try:
            canonical.relative_to(root)
            return str(canonical)
        except ValueError:
            continue

    raise PermissionError(
        f'path {canonical} is outside PETP_PATH_ALLOW_ROOTS '
        f'({[str(r) for r in roots]})'
    )


def reset_cache_for_tests() -> None:
    """Test helper: drop cached roots so tests can mutate the env var."""
    global _resolved_roots
    _resolved_roots = None
