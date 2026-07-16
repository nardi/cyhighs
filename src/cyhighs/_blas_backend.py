"""Select the BLAS/LAPACK backend HiGHS's HiPO solver forwards to.

On Linux and Windows, the compiled `_core` extension links HiGHS/HiPO against
libblastrampoline (lbt), a small shared library that forwards BLAS/LAPACK
calls, at runtime, to whichever real implementation is named by the
`LBT_DEFAULT_LIBS` environment variable. This module sets that variable,
before `_core` is imported, to:

- Intel MKL, if the optional `cyhighs[mkl]` extra is installed and its shared
  library can be found (Linux x86_64 / Windows x86_64 only -- Intel has never
  published MKL for macOS or for ARM);
- otherwise, the OpenBLAS bundled inside this wheel, so cyhighs keeps working
  with zero configuration and no external dependencies by default.

An `LBT_DEFAULT_LIBS` already set in the environment is left untouched, so
advanced users can point HiGHS at any other lbt-compatible BLAS themselves.

On macOS, this module does nothing. HiGHS unconditionally links Apple's
Accelerate framework there instead of going through lbt (see the BLAS/LAPACK
section of the top-level CMakeLists.txt), so there is no backend for
`LBT_DEFAULT_LIBS` to select.
"""

from __future__ import annotations

import glob
import os
import sys
from pathlib import Path


def _locate_mkl() -> str | None:
    """Return the path to Intel MKL's runtime library, if installed.

    The `mkl` PyPI package ships no importable Python module -- it is a
    data-only wheel that drops shared libraries directly under the
    environment's install prefix (`<prefix>/lib` on Linux,
    `<prefix>/Library/bin` on Windows).
    """
    if sys.platform == "win32":
        pattern = str(Path(sys.prefix, "Library", "bin", "mkl_rt*.dll"))
    else:
        pattern = str(Path(sys.prefix, "lib", "libmkl_rt.so*"))

    matches = sorted(glob.glob(pattern))
    return matches[0] if matches else None


def _locate_bundled_openblas() -> str | None:
    """Return the path to the OpenBLAS shared library bundled in this wheel.

    The wheel-repair tools (auditwheel/delvewheel) relocate bundled shared
    libraries into a hash-suffixed sibling directory, so the exact filename
    is discovered with a glob rather than assumed.
    """
    package_dir = Path(__file__).parent
    if sys.platform == "win32":
        # conda-forge's OpenBLAS DLL has no "lib" prefix (openblas.dll), unlike
        # its Linux build, confirmed by extracting the real package.
        pattern_name = "openblas*.dll"
    else:
        pattern_name = "libopenblas*.so*"

    for directory in (package_dir, package_dir.parent / "cyhighs.libs"):
        matches = sorted(glob.glob(str(directory / pattern_name)))
        if matches:
            return matches[0]
    return None


def select_blas_backend() -> None:
    """Set `LBT_DEFAULT_LIBS` before `_core` (and its lbt dependency) load."""
    if sys.platform == "darwin" or "LBT_DEFAULT_LIBS" in os.environ:
        return

    backend = _locate_mkl() or _locate_bundled_openblas()
    if backend is not None:
        os.environ["LBT_DEFAULT_LIBS"] = backend
