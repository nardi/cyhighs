"""Select the BLAS/LAPACK backend HiGHS's HiPO solver forwards to.

On Linux and Windows, the compiled `_core` extension links HiGHS/HiPO against
libblastrampoline (lbt), a small shared library that forwards BLAS/LAPACK
calls, at runtime, to whichever real implementation lbt has been pointed at.
After `_core` (and therefore lbt) is loaded, this module calls lbt's own
`lbt_forward` C API to register a backend:

- Intel MKL, if the optional `cyhighs[mkl]` extra is installed and its shared
  library can be found (Linux x86_64 and Windows x86_64 only, since Intel has
  never published MKL for macOS or for ARM)
- otherwise, the OpenBLAS bundled alongside cyhighs, so cyhighs keeps working
  with zero configuration and no external dependencies by default.

`lbt_forward` is used in preference to lbt's `LBT_DEFAULT_LIBS` environment
variable because a value set through Python's `os.environ` is not reliably
seen by lbt's own `getenv` on Windows (Python and the MinGW-built lbt can use
different C runtimes), which leaves HiPO with no backend and crashing at solve
time. Calling the C API configures the exact lbt instance already loaded into
the process, with no dependence on environment-variable propagation.

If `LBT_DEFAULT_LIBS` is already set in the environment, it is respected and
this module does nothing, so advanced users can still point HiGHS at any other
lbt-compatible BLAS themselves.

On macOS, this module does nothing. HiGHS unconditionally links Apple's
Accelerate framework there instead of going through lbt (see the BLAS/LAPACK
section of the top-level CMakeLists.txt), so there is no backend to register.

A build compiled with CMake's CYHIGHS_USE_LBT off (see CMakeLists.txt) links
OpenBLAS directly with no lbt in the process at all, for local A/B testing
against the default lbt-forwarded build. This module also does nothing there,
since there is no lbt to configure and HiGHS already has a working BLAS
backend linked in directly.
"""

from __future__ import annotations

import ctypes
import glob
import importlib.util
import os
import sys
from pathlib import Path


def _core_dir() -> Path:
    """Return the directory that holds the compiled `_core` extension.

    The bundled BLAS libraries are installed next to `_core`, which is not
    necessarily next to this source file: in an editable install the compiled
    extension lives in the build directory while these `.py` sources are
    imported from `src/cyhighs`. Locating `_core` by its import spec finds the
    right directory in both the editable and the installed-wheel layouts.
    """
    spec = importlib.util.find_spec("cyhighs._core")
    if spec is not None and spec.origin:
        return Path(spec.origin).parent
    return Path(__file__).parent


def _first_match(directories: tuple[Path, ...], pattern_name: str) -> str | None:
    for directory in directories:
        matches = sorted(glob.glob(str(directory / pattern_name)))
        if matches:
            return matches[0]
    return None


def _locate_mkl() -> str | None:
    """Return the path to Intel MKL's runtime library, if installed.

    The `mkl` PyPI package ships no importable Python module. It is a
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
    """Return the path to the OpenBLAS shared library bundled with cyhighs.

    OpenBLAS is installed next to `_core`. The wheel-repair tools
    (auditwheel/delvewheel) may additionally relocate a copy into a
    hash-suffixed sibling directory, so both locations are searched.
    """
    core_dir = _core_dir()
    # conda-forge's OpenBLAS DLL has no "lib" prefix (openblas.dll) on Windows,
    # unlike its Linux build, confirmed by extracting the real packages.
    pattern_name = "openblas*.dll" if sys.platform == "win32" else "libopenblas*.so*"
    return _first_match((core_dir, core_dir.parent / "cyhighs.libs"), pattern_name)


def _lbt_present() -> bool:
    """Return whether this build links against libblastrampoline at all.

    A CYHIGHS_USE_LBT=OFF build (see CMakeLists.txt) links OpenBLAS directly,
    so no lbt files exist next to `_core` at all. That is a normal, expected
    build configuration and not a broken lbt install, so it is checked
    separately from `_open_loaded_lbt` returning None, which does mean lbt
    should be present but could not be located.
    """
    core_dir = _core_dir()
    search_dirs = (core_dir, core_dir.parent / "cyhighs.libs")
    pattern_name = "*blastrampoline*.dll" if sys.platform == "win32" else "libblastrampoline.so*"
    return _first_match(search_dirs, pattern_name) is not None


def _open_loaded_lbt() -> ctypes.CDLL | None:
    """Return a handle to the libblastrampoline `_core` already loaded.

    Importing `_core` pulls lbt into the process as a dependency. It is
    essential to operate on that exact instance rather than load another copy:
    a wheel can contain two lbt files (one installed next to `_core`, another
    that auditwheel/delvewheel vendored into the `*.libs` directory that
    `_core` actually links), and loading a second lbt corrupts its PLT
    trampoline resolution and segfaults on x86_64 (confirmed by a real CI
    crash at the `lbt_forward` call).

    On Linux, `RTLD_NOLOAD` returns the resident library's handle without
    loading anything new. On Windows, `GetModuleHandleW` returns the handle of
    an already-loaded module by name (without a fresh `LoadLibrary`), which is
    then wrapped as a ctypes handle.
    """
    core_dir = _core_dir()
    search_dirs = (core_dir, core_dir.parent / "cyhighs.libs")

    if sys.platform == "win32":
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetModuleHandleW.restype = ctypes.c_void_p
        kernel32.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
        # The DLL may be loaded under its plain name (unrepaired build) or the
        # mangled name delvewheel gives it in the wheel, so match against
        # whatever blastrampoline DLLs are actually present next to _core or
        # in *.libs.
        names: list[str] = []
        for directory in search_dirs:
            for match in sorted(glob.glob(str(directory / "*blastrampoline*.dll"))):
                name = os.path.basename(match)
                if name not in names:
                    names.append(name)
        for name in (*names, "blastrampoline.dll", "libblastrampoline-5.dll"):
            handle = kernel32.GetModuleHandleW(name)
            if handle:
                try:
                    return ctypes.CDLL(name, handle=handle)
                except OSError:
                    continue
        return None

    # Linux: bind to the already-resident instance by its soname, never a copy.
    sonames: list[str] = []
    for directory in search_dirs:
        for match in sorted(glob.glob(str(directory / "libblastrampoline.so*"))):
            name = os.path.basename(match)
            if name not in sonames:
                sonames.append(name)
    # Prefer a versioned soname (libblastrampoline.so.5) over a bare .so symlink,
    # since the versioned name is what the loader tracks the library under.
    sonames.sort(key=lambda name: (".so." not in name, name))
    for name in (*sonames, "libblastrampoline.so.5", "libblastrampoline.so"):
        try:
            return ctypes.CDLL(name, mode=os.RTLD_NOLOAD)
        except OSError:
            continue
    return None


def configure_blas_backend() -> None:
    """Point the already-loaded libblastrampoline at cyhighs's BLAS backend.

    Called after `_core` is imported, so lbt is already in the process. Does
    nothing on macOS (no lbt), on a CYHIGHS_USE_LBT=OFF build (also no lbt),
    or if the user has set `LBT_DEFAULT_LIBS` (respecting their choice).
    """
    if sys.platform == "darwin" or "LBT_DEFAULT_LIBS" in os.environ:
        return
    if not _lbt_present():
        return

    debug = bool(os.environ.get("CYHIGHS_LBT_DEBUG"))
    preferred_backend = str(os.environ.get("CYHIGHS_LBT_PREFER"))

    mkl = _locate_mkl()
    openblas = _locate_bundled_openblas()

    # Select the backend based on user preference, or by default, prefer MKL if
    # installed.
    if preferred_backend.lower() == "mkl":
        backend = mkl or openblas
    elif preferred_backend.lower() == "openblas":
        backend = openblas
    else:
        backend = mkl or openblas

    lbt = _open_loaded_lbt()
    if debug:
        print(f"cyhighs: BLAS backend={backend!r} lbt={lbt!r}", file=sys.stderr)

    if backend is None or lbt is None:
        # A silent missing backend would surface as a crash the first time HiPO
        # calls BLAS, so warn instead of failing quietly.
        print(
            f"cyhighs: could not configure a BLAS backend "
            f"(backend={backend!r}, lbt={lbt!r}), the HiPO solver may be unavailable.",
            file=sys.stderr,
        )
        return

    try:
        # int32_t lbt_forward(const char* libname, int32_t clear, int32_t verbose,
        #                     const char* suffix_hint)
        # All four arguments are required. Passing only three left the final
        # (pointer) argument as an uninitialized register: harmless by luck on
        # the System V AMD64 ABI (Linux/macOS), but a garbage non-NULL pointer
        # that lbt dereferenced and crashed on the Windows x64 ABI. suffix_hint
        # is NULL so lbt auto-detects the symbol suffix.
        lbt.lbt_forward.argtypes = [
            ctypes.c_char_p,
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_char_p,
        ]
        lbt.lbt_forward.restype = ctypes.c_int32
        # clear=1 replaces any existing forwards. verbose is on under CYHIGHS_LBT_DEBUG.
        nforwarded = lbt.lbt_forward(os.fsencode(backend), 1, 1 if debug else 0, None)
        if debug:
            print(f"cyhighs: lbt_forward returned {nforwarded}", file=sys.stderr)
    except (OSError, AttributeError):
        # lbt does not export lbt_forward. Leave it on its own compiled-in
        # fallback rather than failing the import.
        pass
