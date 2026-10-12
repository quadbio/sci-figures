"""Install Arial for matplotlib without system privileges.

Usage (once per machine):
    python -m scifig.fonts            # installs into ~/.local/share/fonts
    python -m scifig.fonts --dir DIR  # custom location; then set SCIFIG_FONT_DIR=DIR

In pixi environments ``pixi add mscorefonts`` works as well; ``apply_style`` finds either. Arial is
Microsoft's, under its own license; this fetches conda-forge's ``mscorefonts`` package.
"""

from __future__ import annotations

import argparse
import io
import tarfile
import urllib.request
from pathlib import Path

# Microsoft core fonts as packaged on conda-forge (noarch).
URL = "https://api.anaconda.org/download/conda-forge/mscorefonts/0.0.1/noarch/mscorefonts-0.0.1-3.tar.bz2"


def install(target: str | Path = "~/.local/share/fonts") -> list[Path]:
    """Download the package and extract Arial (regular, bold, italic, bold italic)."""
    target = Path(target).expanduser()
    target.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL) as r:
        data = r.read()
    out = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:bz2") as tar:
        for m in tar.getmembers():
            name = Path(m.name).name
            if name.lower() in {"arial.ttf", "arialbd.ttf", "ariali.ttf", "arialbi.ttf"}:
                dest = target / name
                dest.write_bytes(tar.extractfile(m).read())
                out.append(dest)
    return out


def main() -> None:
    """Install Arial from the command line."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", default="~/.local/share/fonts")
    args = parser.parse_args()
    for p in install(args.dir):
        print(f"installed {p}")


if __name__ == "__main__":
    main()
