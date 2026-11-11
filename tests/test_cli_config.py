"""CLI regression tests: invalid config must fail cleanly, not traceback."""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Point the config dir at a temp dir BEFORE importing the package, since
# importing anki_packager auto-creates the user config on first import.
os.environ["APPDATA"] = tempfile.mkdtemp(prefix="anki-packager-test-")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

import anki_packager.utils as utils
from anki_packager import cli


def _write_config(text: str) -> None:
    config_path = os.path.join(utils.get_user_config_dir(), "config")
    os.makedirs(config_path, exist_ok=True)
    with open(os.path.join(config_path, "config.toml"), "w", encoding="utf-8") as f:
        f.write(text)


def _run_main(argv):
    old_argv = sys.argv
    sys.argv = argv
    try:
        asyncio.run(cli.main())
    finally:
        sys.argv = old_argv


def test_incomplete_config_exits_cleanly():
    _write_config("[other]\nfoo = 1\n")
    with pytest.raises(SystemExit) as exc:
        _run_main(["prog", "--word", "hello"])
    assert exc.value.code == 1


def test_malformed_config_exits_cleanly():
    _write_config("[[[not toml\n")
    with pytest.raises(SystemExit) as exc:
        _run_main(["prog", "--word", "hello"])
    assert exc.value.code == 1
