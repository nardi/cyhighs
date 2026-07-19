"""Select the BLAS/LAPACK backend HiGHS's HiPO solver forwards to.

The compiled `_core` extension links HiGHS as a prebuilt binary through the
HiGHS_jll Julia package (see meson.build and subprojects/), which brings in
libblastrampoline (lbt), a small shared library that forwards BLAS/LAPACK
calls, at runtime, to whichever real implementation lbt has been pointed at,
on every platform HiGHS_jll publishes. After `_core` (and therefore lbt) is
loaded, this module calls lbt's own `lbt_forward` C API to register the first
available backend from this order of preference:

- Apple's Accelerate framework, on macOS, where it ships with the OS and is
  faster than a bundled OpenBLAS;
- Intel MKL, if the optional `cyhighs[mkl]` extra is installed and its shared
  library can be found (Linux x86_64 and Windows x86_64 only, since Intel has
  never published MKL for macOS or for ARM);
- otherwise the OpenBLAS bundled alongside cyhighs (the OpenBLAS32_jll
  dependency in meson.build, bundled on every platform), so cyhighs keeps
  working with zero configuration and no external dependencies by default.

`CYHIGHS_LBT_PREFER` moves one backend (`accelerate`, `mkl`, or `openblas`) to
the front of that order. `lbt_forward` is used in preference to lbt's own
`LBT_DEFAULT_LIBS` environment variable because a value set through Python's
`os.environ` is not reliably seen by lbt's own `getenv` on Windows (Python and
the MinGW-built lbt can use different C runtimes), which leaves HiPO with no
backend and crashing at solve time. Calling the C API configures the exact lbt
instance already loaded into the process. If `LBT_DEFAULT_LIBS` is already set,
it is respected and this module does nothing.
"""

from __future__ import annotations

import ctypes
import glob
import importlib.util
import json
import os
import sys
from pathlib import Path

_ACCELERATE = "/System/Library/Frameworks/Accelerate.framework/Accelerate"
_BACKEND_ORDER = ("accelerate", "mkl", "openblas")


def _core_dir() -> Path:
    """Return the directory that holds the compiled `_core` extension.

    The bundled BLAS libraries sit next to `_core`, which is not necessarily
    next to this source file: in an editable install the compiled extension
    lives in the meson build directory while these `.py` sources are imported
    from `src/cyhighs`. Locating `_core` by its import spec finds the right
    directory in both the editable and the installed-wheel layouts.
    """
    spec = importlib.util.find_spec("cyhighs._core")
    if spec is not None and spec.origin:
        return Path(spec.origin).parent
    return Path(__file__).parent


def _plan_libdirs(build_dir: Path) -> list[Path]:
    """Return the `{libdir}` source directories from a meson install plan.

    An editable install never runs `meson install`: the JLL runtime libraries
    are never copied anywhere, they stay wherever meson-jll's wrap extracted
    them, under per-platform-triplet directory names inside subprojects/.
    Rather than guess those names, read them back out of the build directory's
    own install plan, the same registry meson-python generates its editable
    loader from.
    """
    plan_path = build_dir / "meson-info" / "intro-install_plan.json"
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [
        Path(source)
        for source, info in plan.get("install_subdirs", {}).items()
        if info.get("destination") == "{libdir}" and Path(source).is_dir()
    ]


def _library_search_dirs() -> tuple[Path, ...]:
    """Return every directory that might hold a JLL-provided runtime library.

    In a built wheel, meson-python bundles them into a `.cyhighs.mesonpy.libs`
    directory next to the `cyhighs` package. In an editable install they stay
    in the subproject directories the install plan points at.
    """
    core_dir = _core_dir()
    return (core_dir, core_dir.parent / ".cyhighs.mesonpy.libs", *_plan_libdirs(core_dir))


def _first_match(pattern_name: str) -> str | None:
    for directory in _library_search_dirs():
        matches = sorted(glob.glob(str(directory / pattern_name)))
        if matches:
            return matches[0]
    return None


def _locate_backend(name: str) -> str | None:
    """Return the shared-library path for a named backend, or None if absent."""
    if name == "accelerate":
        # Accelerate ships with every macOS system, so its presence doubles as
        # the "are we on macOS" test.
        return _ACCELERATE if os.path.exists(_ACCELERATE) else None
    if name == "mkl":
        # The `mkl` PyPI package is a data-only wheel with no importable
        # module; it drops its shared libraries under the environment prefix.
        if sys.platform == "win32":
            pattern = str(Path(sys.prefix, "Library", "bin", "mkl_rt*.dll"))
        else:
            pattern = str(Path(sys.prefix, "lib", "libmkl_rt.so*"))
        matches = sorted(glob.glob(pattern))
        return matches[0] if matches else None
    if name == "openblas":
        suffix = "libopenblas*.dll" if sys.platform == "win32" else "libopenblas*.so*"
        return _first_match(suffix)
    return None


def _open_loaded_lbt() -> ctypes.CDLL | None:
    """Return a handle to the libblastrampoline `_core` already loaded.

    Importing `_core` pulls lbt into the process as a dependency. It is
    essential to operate on that exact instance rather than load another copy:
    a wheel can contain two lbt files (one meson-python placed in
    `.cyhighs.mesonpy.libs`, another that auditwheel/delvewheel additionally
    vendored while repairing it), and loading a second lbt corrupts its PLT
    trampoline resolution and segfaults on x86_64 (confirmed by a real CI
    crash at the `lbt_forward` call).

    On Windows, `GetModuleHandleW` returns the handle of an already-loaded
    module by name without a fresh `LoadLibrary`. On Linux and macOS,
    `RTLD_NOLOAD` returns the resident library's handle without loading
    anything new.
    """
    if sys.platform == "win32":
        glob_pattern, fallbacks = "*blastrampoline*.dll", ("libblastrampoline-5.dll",)
    elif sys.platform == "darwin":
        glob_pattern, fallbacks = "libblastrampoline*.dylib", ("libblastrampoline.dylib",)
    else:
        glob_pattern, fallbacks = "libblastrampoline.so*", ("libblastrampoline.so.5",)

    # The library may be loaded under its plain name or a name mangled by
    # auditwheel/delvewheel, so match against whatever is actually present.
    names: list[str] = []
    for directory in _library_search_dirs():
        for match in sorted(glob.glob(str(directory / glob_pattern))):
            name = os.path.basename(match)
            if name not in names:
                names.append(name)
    # Prefer a versioned soname (libblastrampoline.so.5) over a bare symlink,
    # since the versioned name is what the loader tracks the library under.
    names.sort(key=lambda name: (".so." not in name, name))

    if sys.platform == "win32":
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetModuleHandleW.restype = ctypes.c_void_p
        kernel32.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
        for name in (*names, *fallbacks):
            handle = kernel32.GetModuleHandleW(name)
            if handle:
                try:
                    return ctypes.CDLL(name, handle=handle)
                except OSError:
                    continue
        return None

    for name in (*names, *fallbacks):
        try:
            return ctypes.CDLL(name, mode=os.RTLD_NOLOAD)
        except OSError:
            continue
    return None


def add_windows_dll_directories() -> None:
    """Extend the DLL search path so `_core` can find its JLL runtime libraries.

    Windows has no RPATH equivalent, so the DLLs meson-python bundled (see
    `tool.meson-python.allow-windows-internal-shared-libs` in pyproject.toml)
    are not found automatically the way they are on Linux/macOS. This is a
    Windows/meson-python limitation, not anything specific to lbt (see:
    https://mesonbuild.com/meson-python/how-to-guides/shared-libraries.html#internal-shared-libraries).
    Must run before `_core` is imported, so it resolves paths from this source
    file's location rather than through `_core_dir`'s import spec.
    """
    if sys.platform != "win32":
        return

    package_dir = Path(__file__).resolve().parent
    wheel_libs_dir = package_dir.parent / ".cyhighs.mesonpy.libs"
    if wheel_libs_dir.is_dir():
        directories = [wheel_libs_dir]
    else:
        directories = [
            libdir
            for build_dir in (package_dir.parents[1] / "build").glob("*")
            for libdir in _plan_libdirs(build_dir)
        ]

    for directory in directories:
        os.add_dll_directory(str(directory))
    # add_dll_directory only covers the search Python does for an extension
    # module's own direct dependencies (here, _core's link against libhighs).
    # lbt loads its chosen backend with a plain Win32 LoadLibrary from C, which
    # ignores add_dll_directory and consults only PATH, so prepend PATH too. A
    # real crash confirmed lbt otherwise cannot resolve OpenBLAS's own
    # dependent libgfortran/libwinpthread DLLs, which live alongside it.
    if directories:
        os.environ["PATH"] = os.pathsep.join(
            (*(str(d) for d in directories), os.environ.get("PATH", ""))
        )


def configure_blas_backend() -> None:
    """Point the already-loaded libblastrampoline at cyhighs's BLAS backend.

    Called after `_core` is imported, so lbt is already in the process. Does
    nothing if the user has set `LBT_DEFAULT_LIBS` (respecting their choice).
    """
    if "LBT_DEFAULT_LIBS" in os.environ:
        return

    debug = bool(os.environ.get("CYHIGHS_LBT_DEBUG"))
    lbt = _open_loaded_lbt()
    if lbt is None:
        # HiGHS_jll links lbt on every platform, so this only happens in a
        # broken install. Warn rather than fail the whole import.
        print(
            "cyhighs: could not open the loaded libblastrampoline instance, "
            "the HiPO solver may be unavailable.",
            file=sys.stderr,
        )
        return

    order = list(_BACKEND_ORDER)
    preferred = os.environ.get("CYHIGHS_LBT_PREFER", "").lower()
    if preferred in order:
        order.sort(key=lambda name: name != preferred)

    for name in order:
        backend = _locate_backend(name)
        if backend is None:
            continue
        if debug:
            print(f"cyhighs: forwarding lbt to {name} backend {backend!r}", file=sys.stderr)
        try:
            # int32_t lbt_forward(const char* libname, int32_t clear,
            #                     int32_t verbose, const char* suffix_hint)
            # All four arguments are required: passing only three left the
            # final pointer as an uninitialized register, harmless by luck on
            # the System V AMD64 ABI but a garbage pointer lbt crashed on under
            # the Windows x64 ABI. suffix_hint is NULL for auto-detection.
            lbt.lbt_forward.argtypes = [
                ctypes.c_char_p,
                ctypes.c_int32,
                ctypes.c_int32,
                ctypes.c_char_p,
            ]
            lbt.lbt_forward.restype = ctypes.c_int32
            nforwarded = lbt.lbt_forward(os.fsencode(backend), 1, 1 if debug else 0, None)
            if debug:
                print(f"cyhighs: lbt_forward returned {nforwarded}", file=sys.stderr)
        except (OSError, AttributeError):
            # lbt does not export lbt_forward. Leave it on its own compiled-in
            # fallback rather than failing the import.
            pass
        return

    # A silent missing backend would surface as a crash the first time HiPO
    # calls BLAS, so warn instead of failing quietly.
    print(
        "cyhighs: could not locate any BLAS backend, the HiPO solver may be unavailable.",
        file=sys.stderr,
    )
