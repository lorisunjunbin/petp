"""Security tests for CMDProcessor.

P0-1: shell=True hardcoded → injection (CWE-78). After fix, default behavior splits
cmdstr via shlex (no shell), so metacharacters become literal arguments — not
shell directives. The PoC writes a marker file via injection; if the file exists,
shell mode was active and injection succeeded.
"""

import json
import os
import sys
import tempfile


def _run_cmd(make_processor, cmdstr, shell=None):
    params = {"cmdstr": cmdstr, "data_key": "_out", "timeout": "10"}
    if shell is not None:
        params["shell"] = shell
    proc = make_processor("CMD", json.dumps(params), {})
    proc.process()
    return proc.get_data("_out")


class TestCMDInjectionDefense:

    def test_default_shlex_blocks_semicolon_command_chain(self, make_processor, tmp_path):
        # Marker file path. If injection succeeds, shell will run `touch` and create it.
        marker = tmp_path / "INJECTED.flag"
        cmd = f"echo safe; touch {marker}"
        # In default (shell=False) mode, the whole thing is passed to echo as args —
        # ';' and 'touch' become literal text, no second command runs.
        out = _run_cmd(make_processor, cmd)
        assert not marker.exists(), "injection succeeded — touch was executed"

    def test_default_shlex_blocks_double_ampersand(self, make_processor, tmp_path):
        marker = tmp_path / "CHAINED.flag"
        cmd = f"echo first && touch {marker}"
        out = _run_cmd(make_processor, cmd)
        assert not marker.exists(), "&& injection succeeded"

    def test_default_shlex_blocks_pipe(self, make_processor, tmp_path):
        marker = tmp_path / "PIPED.flag"
        # `tee` would write to the file if the pipe were honored.
        cmd = f"echo data | tee {marker}"
        out = _run_cmd(make_processor, cmd)
        assert not marker.exists(), "pipe injection succeeded"

    def test_simple_command_still_works(self, make_processor):
        out = _run_cmd(make_processor, "echo hello")
        assert out.strip() == "hello"

    def test_shell_yes_opt_in_enables_metacharacters(self, make_processor, tmp_path):
        # When user explicitly opts in, shell metacharacters work — by design.
        if sys.platform == "win32":
            return  # cmd.exe shell semantics differ
        marker = tmp_path / "OPTIN.flag"
        cmd = f"echo first; touch {marker}"
        out = _run_cmd(make_processor, cmd, shell="yes")
        assert marker.exists(), "shell=yes should run the second command"

    def test_shell_no_explicit_blocks_injection(self, make_processor, tmp_path):
        marker = tmp_path / "EXPLICIT.flag"
        cmd = f"echo plain; touch {marker}"
        out = _run_cmd(make_processor, cmd, shell="no")
        assert not marker.exists()

    def test_shell_yes_case_insensitive(self, make_processor, tmp_path):
        # "YES" / "Yes" should also opt into shell.
        if sys.platform == "win32":
            return
        marker = tmp_path / "YESCASE.flag"
        cmd = f"echo a; touch {marker}"
        out = _run_cmd(make_processor, cmd, shell="YES")
        assert marker.exists()
