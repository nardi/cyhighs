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
so this has to be cleaned up before the extension is ever loaded.

Run as a meson.add_install_script(), so it applies uniformly whether meson
install is invoked to populate a wheel (cibuildwheel) or a normal,
non-editable `pip`/`uv` install -- both are the same underlying operation
from meson's point of view, and both are affected.
"""

from __future__ import annotations

import glob
import os
import subprocess
import sys


def _rpaths(path: str) -> list[str]:
    out = subprocess.run(["otool", "-l", path], capture_output=True, text=True, check=True).stdout
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
                rpaths.append(path_line[len("path "):].rsplit(" (offset", 1)[0].strip())
    return rpaths


def _dedupe(path: str) -> None:
    seen: set[str] = set()
    for rpath in _rpaths(path):
        if rpath in seen:
            subprocess.run(["install_name_tool", "-delete_rpath", rpath, path], check=True)
        else:
            seen.add(rpath)


def main() -> None:
    if sys.platform != "darwin":
        return
    destdir = os.environ.get("MESON_INSTALL_DESTDIR_PREFIX") or os.environ["MESON_INSTALL_PREFIX"]
    for so_path in glob.glob(os.path.join(destdir, "**", "_core*.so"), recursive=True):
        _dedupe(so_path)


if __name__ == "__main__":
    main()
