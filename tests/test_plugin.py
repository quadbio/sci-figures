"""The plugin manifest and the Python package describe the same release."""

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_versions_agree():
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    package = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert plugin["version"] == package["version"]


def test_setup_pins_this_release():
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    setup = (ROOT / "skills" / "sci-figures" / "references" / "setup.md").read_text()
    assert f'tag = "v{version}"' in setup and f"sci-figures@v{version}" in setup
