"""Tests for utils/SafePaths.py — Phase 2 P1-2 path traversal guard.

Default-off design: PETP_PATH_ALLOW_ROOTS unset → validate_path() canonicalizes
but never rejects, preserving existing yaml behavior. When set, paths must
resolve under one of the listed roots.
"""
import os
import sys

import pytest

from utils import SafePaths


@pytest.fixture(autouse=True)
def _reset_cache():
    SafePaths.reset_cache_for_tests()
    yield
    SafePaths.reset_cache_for_tests()


class TestGuardOffByDefault:

    def test_no_env_var_canonicalizes_only(self, monkeypatch, tmp_path):
        monkeypatch.delenv("PETP_PATH_ALLOW_ROOTS", raising=False)
        f = tmp_path / "a.txt"
        f.write_text("x")
        assert SafePaths.validate_path(str(f)) == str(f.resolve())

    def test_no_env_var_accepts_any_path(self, monkeypatch):
        monkeypatch.delenv("PETP_PATH_ALLOW_ROOTS", raising=False)
        # /etc/passwd may not exist on Windows but resolve() does not require it
        result = SafePaths.validate_path("/etc/passwd")
        assert result.endswith("passwd") or result.endswith("passwd")  # canonical form

    def test_empty_env_var_treated_as_off(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PETP_PATH_ALLOW_ROOTS", "")
        f = tmp_path / "b.txt"
        f.write_text("x")
        assert SafePaths.validate_path(str(f)) == str(f.resolve())

    def test_is_guard_active_false_when_unset(self, monkeypatch):
        monkeypatch.delenv("PETP_PATH_ALLOW_ROOTS", raising=False)
        assert SafePaths.is_guard_active() is False


class TestGuardOnRejectsTraversal:

    def test_path_under_root_allowed(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PETP_PATH_ALLOW_ROOTS", str(tmp_path))
        SafePaths.reset_cache_for_tests()
        f = tmp_path / "ok.txt"
        f.write_text("x")
        assert SafePaths.validate_path(str(f)) == str(f.resolve())

    def test_path_outside_root_rejected(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PETP_PATH_ALLOW_ROOTS", str(tmp_path))
        SafePaths.reset_cache_for_tests()
        outside = tmp_path.parent / "outside.txt"
        with pytest.raises(PermissionError, match="outside PETP_PATH_ALLOW_ROOTS"):
            SafePaths.validate_path(str(outside))

    def test_path_traversal_rejected(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PETP_PATH_ALLOW_ROOTS", str(tmp_path))
        SafePaths.reset_cache_for_tests()
        # ..  escapes root → resolved sits outside tmp_path
        attack = tmp_path / ".." / ".." / "etc" / "passwd"
        with pytest.raises(PermissionError):
            SafePaths.validate_path(str(attack))

    def test_multiple_roots_any_match_passes(self, monkeypatch, tmp_path):
        root_a = tmp_path / "a"
        root_b = tmp_path / "b"
        root_a.mkdir()
        root_b.mkdir()
        sep = ";" if os.name == "nt" else ":"
        monkeypatch.setenv("PETP_PATH_ALLOW_ROOTS", f"{root_a}{sep}{root_b}")
        SafePaths.reset_cache_for_tests()
        f = root_b / "ok.txt"
        f.write_text("x")
        assert SafePaths.validate_path(str(f)) == str(f.resolve())

    def test_is_guard_active_true_when_set(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PETP_PATH_ALLOW_ROOTS", str(tmp_path))
        SafePaths.reset_cache_for_tests()
        assert SafePaths.is_guard_active() is True


class TestEdgeCases:

    def test_empty_path_raises_value_error(self, monkeypatch):
        monkeypatch.delenv("PETP_PATH_ALLOW_ROOTS", raising=False)
        with pytest.raises(ValueError, match="must not be empty"):
            SafePaths.validate_path("")

    def test_tilde_expanded(self, monkeypatch, tmp_path):
        monkeypatch.delenv("PETP_PATH_ALLOW_ROOTS", raising=False)
        result = SafePaths.validate_path("~")
        assert os.path.expanduser("~") in result

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX symlink only")
    def test_symlink_resolved_then_checked(self, monkeypatch, tmp_path):
        real_root = tmp_path / "real"
        real_root.mkdir()
        link_root = tmp_path / "link"
        link_root.symlink_to(real_root)
        outside = tmp_path / "outside"
        outside.mkdir()
        link_to_outside = real_root / "to_outside"
        link_to_outside.symlink_to(outside)

        monkeypatch.setenv("PETP_PATH_ALLOW_ROOTS", str(real_root))
        SafePaths.reset_cache_for_tests()

        # symlink leaving root → rejected because resolve() follows it
        with pytest.raises(PermissionError):
            SafePaths.validate_path(str(link_to_outside))
