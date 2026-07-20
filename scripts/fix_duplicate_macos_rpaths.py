#!/usr/bin/env python3
"""Collapse duplicate LC_RPATH entries left behind by meson-python on macOS.

_core links against several JLL-provided libraries (HiGHS, OpenBLAS32, Zlib,
...), each living in its own distinct subproject build directory. Meson adds
one build-tree, @loader_path-relative LC_RPATH entry per distinct directory.
meson-python's own install-time fix-up (mesonpy._rpath.fix_rpath) rewrites
every entry starting with "@loader_path/" to the same final destination
(the wheel's bundled-libs folder), so those distinct originals collapse into
several byte-identical LC_RPATH commands. Modern dyld refuses to dlopen a
Mach-O binary with duplicate LC_RPATH entries at all ("duplicate LC_RPATH"),
so this has to be cleaned up after the fact, wherever a `_core` extension
module ends up: inside a just-built wheel (see wheels.yml, run as an extra
step in CIBW_REPAIR_WHEEL_COMMAND_MACOS, after delocate) or a normal,
non-editable dev install (see tests.yml, run directly against the installed
.venv copy). Both go through the exact same meson-python codepath and are
affected identically.

Usage: fix_duplicate_macos_rpaths.py PATH...
Each PATH is either a `_core*.so` file (fixed in place) or a `.whl` file
(the wheel is rewritten in place with its `_core*.so` member fixed).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def _rpaths(path: Path) -> list[str]:
    result = subprocess.run(["otool", "-l", str(path)], capture_output=True, text=True, check=True)
    out = result.stdout
    lines = out.splitlines()
    rpaths = []
    for i, line in enumerate(lines):
        if line.strip() == "cmd LC_RPATH":
            # The path is two lines below "cmd LC_RPATH":
            #   cmd LC_RPATH
            #   cmdsize NN
            #   path <value> (offset NN)
            path_line = lines[i + 2].strip()
            if path_line.startswith("path "):
                rpaths.append(path_line[len("path ") :].rsplit(" (offset", 1)[0].strip())
    return rpaths


def dedupe_file(path: Path) -> bool:
    """Remove duplicate LC_RPATH entries from a Mach-O file. Returns whether any were removed."""
    seen: set[str] = set()
    changed = False
    for rpath in _rpaths(path):
        if rpath in seen:
            subprocess.run(["install_name_tool", "-delete_rpath", rpath, str(path)], check=True)
            changed = True
        else:
            seen.add(rpath)
    return changed


def dedupe_wheel(wheel_path: Path) -> None:
    """Rewrite a wheel in place with any bundled `_core*.so` member's rpath de-duplicated."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        with zipfile.ZipFile(wheel_path) as whl:
            names = whl.namelist()
            whl.extractall(tmp)

        touched = False
        for so_path in tmp.rglob("_core*.so"):
            touched |= dedupe_file(so_path)

        if not touched:
            return

        fixed_wheel = tmp_str + ".whl"
        with zipfile.ZipFile(fixed_wheel, "w", zipfile.ZIP_DEFLATED) as out:
            for name in names:
                out.write(tmp / name, name)
        shutil.move(fixed_wheel, wheel_path)


def main() -> None:
    """Dedupe LC_RPATH entries in each path given on the command line."""
    if sys.platform != "darwin":
        return
    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.suffix == ".whl":
            dedupe_wheel(path)
        else:
            dedupe_file(path)


if __name__ == "__main__":
    main()
