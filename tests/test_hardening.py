"""Tests for hardened error-handling paths in cognis_setup and webhook."""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from unittest import mock

# ---------------------------------------------------------------------------
# webhook tests
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "integrations"))

from integrations.webhook import main as webhook_main, _validate_url  # noqa: E402


class TestValidateUrl:
    def test_empty_url_returns_error(self):
        assert _validate_url("") is not None

    def test_no_scheme_returns_error(self):
        assert _validate_url("example.com/hook") is not None

    def test_ftp_scheme_returns_error(self):
        assert _validate_url("ftp://example.com/hook") is not None

    def test_http_url_is_valid(self):
        assert _validate_url("http://example.com/hook") is None

    def test_https_url_is_valid(self):
        assert _validate_url("https://example.com/hook") is None


class TestWebhookMain:
    def _run(self, argv, stdin_text):
        """Run webhook main() with mocked stdin, return (exit_code, stdout, stderr)."""
        out = io.StringIO()
        err = io.StringIO()
        with (
            mock.patch("sys.stdin", io.StringIO(stdin_text)),
            mock.patch("sys.stdout", out),
            mock.patch("sys.stderr", err),
        ):
            code = webhook_main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_empty_stdin_returns_exit_2(self):
        code, _, err = self._run(["--url", "https://example.com/hook"], "")
        assert code == 2
        assert "empty" in err.lower() or "stdin" in err.lower()

    def test_whitespace_only_stdin_returns_exit_2(self):
        code, _, err = self._run(["--url", "https://example.com/hook"], "   \n  ")
        assert code == 2

    def test_invalid_json_stdin_returns_exit_2(self):
        code, _, err = self._run(
            ["--url", "https://example.com/hook"], "{not valid json}"
        )
        assert code == 2
        assert "json" in err.lower()

    def test_bad_url_scheme_returns_exit_2(self):
        code, _, err = self._run(
            ["--url", "ftp://example.com/hook"], '{"ok": true}'
        )
        assert code == 2
        assert "url" in err.lower() or "http" in err.lower()

    def test_malformed_header_returns_exit_2(self):
        code, _, err = self._run(
            ["--url", "https://example.com/hook", "--header", "BadHeader"],
            '{"ok": true}',
        )
        assert code == 2
        assert "header" in err.lower()

    def test_valid_payload_posts_and_returns_0(self):
        """With a valid URL + valid JSON, a successful HTTP call returns 0."""

        class FakeResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

        with mock.patch(
            "urllib.request.urlopen", return_value=FakeResponse()
        ) as mock_open:
            out = io.StringIO()
            with (
                mock.patch("sys.stdin", io.StringIO('{"result": "ok"}')),
                mock.patch("sys.stdout", out),
            ):
                code = webhook_main(["--url", "https://example.com/hook"])
        assert code == 0
        assert mock_open.called
        out_text = out.getvalue()
        assert "posted" in out_text


# ---------------------------------------------------------------------------
# cognis_setup tests
# ---------------------------------------------------------------------------
import cognis_setup  # noqa: E402


class TestGuide:
    def test_normal_level(self):
        mapping = {1: "basic", 3: "intermediate", 5: "expert"}
        assert cognis_setup.guide(1, mapping) == "basic"
        assert cognis_setup.guide(3, mapping) == "intermediate"
        assert cognis_setup.guide(5, mapping) == "expert"

    def test_level_below_minimum_uses_lowest_anchor(self):
        mapping = {2: "two", 4: "four"}
        # Level 0 should clamp to 1; 1 < 2 so falls back to lowest anchor (2).
        assert cognis_setup.guide(0, mapping) == "two"

    def test_level_above_maximum_uses_highest_anchor(self):
        mapping = {1: "one", 3: "three"}
        assert cognis_setup.guide(99, mapping) == "three"

    def test_non_integer_level_uses_default(self):
        mapping = {1: "one", 3: "three", 5: "five"}
        # A string level from a corrupted state file should not crash.
        result = cognis_setup.guide("not-a-number", mapping)
        assert isinstance(result, str)

    def test_empty_mapping_returns_empty_string(self):
        assert cognis_setup.guide(3, {}) == ""


class TestLoadState:
    def test_corrupt_json_returns_empty_dict(self, tmp_path, monkeypatch):
        state_dir = tmp_path / ".cognis"
        state_dir.mkdir()
        state_file = state_dir / "setup.json"
        state_file.write_text("NOT_JSON", encoding="utf-8")
        monkeypatch.setattr(cognis_setup, "STATE_FILE", state_file)
        assert cognis_setup.load_state() == {}

    def test_non_dict_json_returns_empty_dict(self, tmp_path, monkeypatch):
        state_dir = tmp_path / ".cognis"
        state_dir.mkdir()
        state_file = state_dir / "setup.json"
        state_file.write_text("[1, 2, 3]", encoding="utf-8")
        monkeypatch.setattr(cognis_setup, "STATE_FILE", state_file)
        assert cognis_setup.load_state() == {}

    def test_invalid_familiarity_is_stripped(self, tmp_path, monkeypatch):
        state_dir = tmp_path / ".cognis"
        state_dir.mkdir()
        state_file = state_dir / "setup.json"
        state_file.write_text(
            json.dumps({"familiarity": "broken", "method": "pip"}),
            encoding="utf-8",
        )
        monkeypatch.setattr(cognis_setup, "STATE_FILE", state_file)
        state = cognis_setup.load_state()
        assert "familiarity" not in state
        assert state.get("method") == "pip"

    def test_out_of_range_familiarity_is_stripped(self, tmp_path, monkeypatch):
        state_dir = tmp_path / ".cognis"
        state_dir.mkdir()
        state_file = state_dir / "setup.json"
        state_file.write_text(
            json.dumps({"familiarity": 99}), encoding="utf-8"
        )
        monkeypatch.setattr(cognis_setup, "STATE_FILE", state_file)
        state = cognis_setup.load_state()
        assert "familiarity" not in state

    def test_valid_state_is_preserved(self, tmp_path, monkeypatch):
        state_dir = tmp_path / ".cognis"
        state_dir.mkdir()
        state_file = state_dir / "setup.json"
        state_file.write_text(
            json.dumps({"familiarity": 3, "method": "pipx"}), encoding="utf-8"
        )
        monkeypatch.setattr(cognis_setup, "STATE_FILE", state_file)
        state = cognis_setup.load_state()
        assert state["familiarity"] == 3
        assert state["method"] == "pipx"


class TestDiscoverManifest:
    def test_nonexistent_explicit_path_returns_none(self, tmp_path, capsys):
        missing = str(tmp_path / "no_such_file.json")
        result = cognis_setup.discover_manifest(missing)
        assert result is None
        captured = capsys.readouterr()
        assert "error" in (captured.err + captured.out).lower()

    def test_existing_explicit_path_returns_path(self, tmp_path):
        mf = tmp_path / "MANIFEST.json"
        mf.write_text('{"tools": []}', encoding="utf-8")
        result = cognis_setup.discover_manifest(str(mf))
        assert result == mf


class TestLoadManifest:
    def test_none_path_returns_empty(self):
        result = cognis_setup.load_manifest(None)
        assert result == {"meta": {}, "tools": {}}

    def test_malformed_json_returns_empty(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{bad json", encoding="utf-8")
        result = cognis_setup.load_manifest(bad)
        assert result == {"meta": {}, "tools": {}}

    def test_empty_tools_list(self, tmp_path):
        mf = tmp_path / "MANIFEST.json"
        mf.write_text('{"tools": []}', encoding="utf-8")
        result = cognis_setup.load_manifest(mf)
        assert result["tools"] == {}

    def test_list_of_tools_parsed(self, tmp_path):
        mf = tmp_path / "MANIFEST.json"
        mf.write_text(
            json.dumps(
                {
                    "tools": [
                        {
                            "name": "depscan",
                            "domain": "Security",
                            "desc": "Dep scanner",
                            "pip": "pip install depscan",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        result = cognis_setup.load_manifest(mf)
        assert "depscan" in result["tools"]
        assert result["tools"]["depscan"]["domain"] == "Security"

    def test_entry_without_name_skipped(self, tmp_path):
        mf = tmp_path / "MANIFEST.json"
        mf.write_text(
            json.dumps({"tools": [{"domain": "X", "desc": "no name here"}]}),
            encoding="utf-8",
        )
        result = cognis_setup.load_manifest(mf)
        assert result["tools"] == {}
