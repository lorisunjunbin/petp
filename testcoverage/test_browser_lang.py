"""Unit tests for headless browser language resolution in
SeleniumUtil.get_webdriver4_chrome() and its plumbing through GO_TO_PAGE.

Resolution order (headless only): explicit browser_lang arg > PETP_BROWSER_LANG
env var > "zh-CN". Headed mode sets no language. These tests mock the driver so
no real Chrome is launched — they only assert the --lang argument built into
ChromeOptions.
"""

import os
from unittest import mock

import pytest

from utils.SeleniumUtil import SeleniumUtil


def _lang_arg(options):
    """Return the value of the --lang=<x> argument, or None if absent."""
    for a in options.arguments:
        if a.startswith("--lang="):
            return a.split("=", 1)[1]
    return None


@pytest.fixture
def capture_options(monkeypatch):
    """Mock chromedriver path + Service + webdriver.Chrome so no browser starts,
    and capture the ChromeOptions passed to webdriver.Chrome."""
    captured = {}

    monkeypatch.setattr(SeleniumUtil, "_resolve_chromedriver_path", staticmethod(lambda: "/tmp/fake-driver"))
    monkeypatch.setattr(SeleniumUtil, "_resolve_chrome_binary", staticmethod(lambda: None))
    monkeypatch.setattr("utils.SeleniumUtil.Service", lambda executable_path=None: object())

    def fake_chrome(options=None, service=None):
        captured["options"] = options
        m = mock.MagicMock()
        return m

    monkeypatch.setattr("utils.SeleniumUtil.webdriver.Chrome", fake_chrome)
    # Force headless so the language branch runs; not in docker path.
    monkeypatch.setattr(SeleniumUtil, "is_running_in_docker", staticmethod(lambda: False))
    monkeypatch.setenv("PETP_HEADLESS", "true")
    return captured


class TestBrowserLangResolution:

    def test_explicit_arg_wins_over_env(self, capture_options, monkeypatch):
        monkeypatch.setenv("PETP_BROWSER_LANG", "zh-CN")
        SeleniumUtil.get_webdriver4_chrome(browser_lang="en-US")
        assert _lang_arg(capture_options["options"]) == "en-US"

    def test_env_used_when_no_arg(self, capture_options, monkeypatch):
        monkeypatch.setenv("PETP_BROWSER_LANG", "ja-JP")
        SeleniumUtil.get_webdriver4_chrome(browser_lang=None)
        assert _lang_arg(capture_options["options"]) == "ja-JP"

    def test_default_zh_cn_when_nothing_set(self, capture_options, monkeypatch):
        monkeypatch.delenv("PETP_BROWSER_LANG", raising=False)
        SeleniumUtil.get_webdriver4_chrome(browser_lang=None)
        assert _lang_arg(capture_options["options"]) == "zh-CN"

    def test_headed_mode_sets_no_lang(self, monkeypatch):
        captured = {}

        def fake_chrome(options=None, service=None):
            captured["options"] = options
            return mock.MagicMock()

        monkeypatch.setattr(SeleniumUtil, "_resolve_chromedriver_path", staticmethod(lambda: "/tmp/fake-driver"))
        monkeypatch.setattr(SeleniumUtil, "_resolve_chrome_binary", staticmethod(lambda: None))
        monkeypatch.setattr("utils.SeleniumUtil.Service", lambda executable_path=None: object())
        monkeypatch.setattr("utils.SeleniumUtil.webdriver.Chrome", fake_chrome)
        monkeypatch.setattr(SeleniumUtil, "is_running_in_docker", staticmethod(lambda: False))
        monkeypatch.delenv("PETP_HEADLESS", raising=False)
        SeleniumUtil.get_webdriver4_chrome(browser_lang="en-US")
        # headed mode: --start-maximized, no --lang
        assert _lang_arg(captured["options"]) is None


class TestGoToPagePlumbing:

    def test_go_to_page_passes_browser_lang(self, make_processor, monkeypatch):
        seen = {}

        def fake_get_page(crmurl, download_folder=None, page_load_timeout=180, browser_lang=None):
            seen["url"] = crmurl
            seen["browser_lang"] = browser_lang
            return mock.MagicMock()

        monkeypatch.setattr(SeleniumUtil, "get_page_from_url", staticmethod(fake_get_page))
        proc = make_processor(
            "GO_TO_PAGE",
            '{"url":"https://example.com","browser_lang":"{lang}","chrome_name":"chrome"}',
            {"lang": "en-US"},
        )
        proc.process()
        assert seen["browser_lang"] == "en-US"

    def test_go_to_page_empty_lang_becomes_none(self, make_processor, monkeypatch):
        seen = {}

        def fake_get_page(crmurl, download_folder=None, page_load_timeout=180, browser_lang=None):
            seen["browser_lang"] = browser_lang
            return mock.MagicMock()

        monkeypatch.setattr(SeleniumUtil, "get_page_from_url", staticmethod(fake_get_page))
        proc = make_processor(
            "GO_TO_PAGE",
            '{"url":"https://example.com","browser_lang":"","chrome_name":"chrome"}',
            {},
        )
        proc.process()
        # empty -> None so SeleniumUtil falls back to env/default
        assert seen["browser_lang"] is None
