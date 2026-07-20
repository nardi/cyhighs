project('HiGHS-x86_64-linux-musl-cxx11', 'c')

cc = meson.get_compiler('c')
# The tarball is never downloaded ahead of time, so whether it ships headers
# is unknown until Meson has actually extracted it. Checking here, after
# extraction, avoids guessing in the generator.
fs = import('fs')
include_dirs = []
if fs.is_dir('include')
  include_dirs = [include_directories('include')]
  # Some JLLs (SuiteSparse and HiGHS both do) namespace their headers under
  # include/<lowercased-package-name>/ instead of flat under include/, to
  # avoid collisions between generically named headers from different JLLs.
  # Nothing in the JLL's own metadata says which convention it follows, so
  # both are added when present, covering `#include <SuiteSparse_config.h>`
  # and `#include <suitesparse/SuiteSparse_config.h>` alike.
  if fs.is_dir('include/highs')
    include_dirs += [include_directories('include/highs')]
  endif
endif



# One cc.find_library() per library this platform's wrapper script
# declares, using the exact path Julia itself records for it.


libhighs = cc.find_library('highs', dirs: meson.current_source_dir() / 'lib')



# Transitive JLL dependencies, resolved the same way this package itself
# is: through their own selector wrap's [provide] fallback.

libblastrampoline_dep = dependency('libblastrampoline')

CompilerSupportLibraries_dep = dependency('CompilerSupportLibraries')

Zlib_dep = dependency('Zlib')


# Install this platform's own runtime libraries, the same as
# `library('z', ..., install: true)` in an ordinary Meson project. They go
# to libdir, which is where meson-python folds a wheel's bundled shared
# libraries from (into `.<project>.mesonpy.libs`), and where an rpath entry
# points on the platforms that have one. On Windows the whole `bin`
# directory is installed rather than only the declared products, because
# the MinGW runtime DLLs those depend on (`libwinpthread-1.dll` and friends,
# provided by CompilerSupportLibraries) ship there without ever being
# declared as products of their own, and would otherwise be left out.


install_data('lib/libhighs.so', install_dir: get_option('libdir'))

# The tarball's lib/libhighs.so is the unversioned dev-time name; the
# library's own embedded DT_SONAME (and therefore the NEEDED entry our
# compiled _core.so records) is the versioned libhighs.so.1, which nothing
# above installs. Without a copy present under that name too, the runtime
# loader (and auditwheel) cannot resolve that reference. install_symlink()
# would be lighter, but its target is invisible to meson's own install-plan
# introspection, which meson-python relies on to decide what goes in the
# wheel, so it is silently dropped there; fs.copyfile() is a real,
# independently-tracked install target instead.
fs.copyfile('lib/libhighs.so', 'libhighs.so.1', install: true, install_dir: get_option('libdir'))



highs_dep = declare_dependency(
  include_directories: include_dirs,
  dependencies: [

    libhighs,


    libblastrampoline_dep,

    CompilerSupportLibraries_dep,

    Zlib_dep,

  ],
)