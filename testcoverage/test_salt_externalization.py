"""Tests for SALT externalization (P0-3).

Default SALT remains 'petpisawesome' for pre-2026-05 ciphertext compatibility,
but operators can override via env PETP_SALT or ~/.petp/secret (mode 0600).
A WARNING is logged when the default falls through.
"""

import logging
import os
import stat
import sys

import pytest

from core.processor import Processor


@pytest.fixture(autouse=True)
def reset_salt_cache(monkeypatch):
    """Force re-resolution before/after each test."""
    Processor._salt_resolved = False
    Processor.SALT = Processor._DEFAULT_SALT
    yield
    Processor._salt_resolved = False
    Processor.SALT = Processor._DEFAULT_SALT


class TestSaltResolution:

    def test_env_var_overrides_default(self, monkeypatch):
        monkeypatch.setenv("PETP_SALT", "my-secret-salt-12345")
        salt = Processor._resolve_salt()
        assert salt == "my-secret-salt-12345"

    def test_default_fallback_when_no_env_no_file(self, monkeypatch, tmp_path, caplog):
        monkeypatch.delenv("PETP_SALT", raising=False)
        monkeypatch.setenv("HOME", str(tmp_path))  # ~/.petp/secret won't exist
        with caplog.at_level(logging.WARNING):
            salt = Processor._resolve_salt()
        assert salt == Processor._DEFAULT_SALT
        # Warning must be emitted to alert operators.
        assert any("DEFAULT public salt" in rec.message for rec in caplog.records)

    def test_secret_file_loaded(self, monkeypatch, tmp_path):
        monkeypatch.delenv("PETP_SALT", raising=False)
        petp_dir = tmp_path / ".petp"
        petp_dir.mkdir()
        secret = petp_dir / "secret"
        secret.write_text("file-based-salt-xyz\n")
        if os.name == "posix":
            os.chmod(secret, 0o600)
        monkeypatch.setenv("HOME", str(tmp_path))
        salt = Processor._resolve_salt()
        assert salt == "file-based-salt-xyz"

    @pytest.mark.skipif(os.name != "posix", reason="POSIX-only mode check")
    def test_secret_file_rejected_when_world_readable(self, monkeypatch, tmp_path, caplog):
        monkeypatch.delenv("PETP_SALT", raising=False)
        petp_dir = tmp_path / ".petp"
        petp_dir.mkdir()
        secret = petp_dir / "secret"
        secret.write_text("insecure-salt\n")
        os.chmod(secret, 0o644)  # world-readable — must be ignored
        monkeypatch.setenv("HOME", str(tmp_path))
        with caplog.at_level(logging.WARNING):
            salt = Processor._resolve_salt()
        assert salt == Processor._DEFAULT_SALT
        assert any("must be 0600" in rec.message for rec in caplog.records)

    def test_env_takes_priority_over_file(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PETP_SALT", "from-env")
        petp_dir = tmp_path / ".petp"
        petp_dir.mkdir()
        secret = petp_dir / "secret"
        secret.write_text("from-file\n")
        if os.name == "posix":
            os.chmod(secret, 0o600)
        monkeypatch.setenv("HOME", str(tmp_path))
        assert Processor._resolve_salt() == "from-env"


class TestEncryptDecryptRoundtrip:

    def test_default_salt_roundtrip(self, monkeypatch):
        monkeypatch.delenv("PETP_SALT", raising=False)
        # Use a tmp HOME to avoid actual ~/.petp/secret affecting test
        monkeypatch.setenv("HOME", "/nonexistent/path/for/test")
        ciphertext = Processor.encrypt_pwd("hello-world")
        plaintext = Processor.decrypt_pwd(ciphertext)
        assert plaintext == "hello-world"

    def test_custom_salt_roundtrip(self, monkeypatch):
        monkeypatch.setenv("PETP_SALT", "my-custom-salt")
        ciphertext = Processor.encrypt_pwd("secret-value")
        plaintext = Processor.decrypt_pwd(ciphertext)
        assert plaintext == "secret-value"

    def test_different_salts_produce_different_ciphertext(self, monkeypatch):
        monkeypatch.setenv("PETP_SALT", "salt-A")
        c1 = Processor.encrypt_pwd("same-input")
        Processor._salt_resolved = False  # force re-resolve
        monkeypatch.setenv("PETP_SALT", "salt-B")
        c2 = Processor.encrypt_pwd("same-input")
        # cryptocode uses random IV anyway — they would differ regardless,
        # but key check is that decrypting c1 with salt-B fails.
        Processor._salt_resolved = False
        result = Processor.decrypt_pwd(c1)
        # cryptocode returns False on auth failure, never the original.
        assert result != "same-input"
