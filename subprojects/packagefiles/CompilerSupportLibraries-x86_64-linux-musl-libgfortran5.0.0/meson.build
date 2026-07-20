project('CompilerSupportLibraries-x86_64-linux-musl-libgfortran5.0.0', 'c')

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
  if fs.is_dir('include/compilersupportlibraries')
    include_dirs += [include_directories('include/compilersupportlibraries')]
  endif
endif



# One cc.find_library() per library this platform's wrapper script
# declares, using the exact path Julia itself records for it.


libatomic = cc.find_library('atomic', dirs: meson.current_source_dir() / 'lib')



libgcc_s = cc.find_library('gcc_s', dirs: meson.current_source_dir() / 'lib')



libgfortran = cc.find_library('gfortran', dirs: meson.current_source_dir() / 'lib')



libgomp = cc.find_library('gomp', dirs: meson.current_source_dir() / 'lib')



libstdcxx = cc.find_library('stdc++', dirs: meson.current_source_dir() / 'lib')



# Transitive JLL dependencies, resolved the same way this package itself
# is: through their own selector wrap's [provide] fallback.


# Install this platform's own runtime libraries, the same as
# `library('z', ..., install: true)` in an ordinary Meson project. They go
# to libdir, which is where meson-python folds a wheel's bundled shared
# libraries from (into `.<project>.mesonpy.libs`), and where an rpath entry
# points on the platforms that have one. On Windows the whole `bin`
# directory is installed rather than only the declared products, because
# the MinGW runtime DLLs those depend on (`libwinpthread-1.dll` and friends,
# provided by CompilerSupportLibraries) ship there without ever being
# declared as products of their own, and would otherwise be left out.


install_data('lib/libatomic.so', install_dir: get_option('libdir'))

# libgcc_s is the one exception in this tarball: lib/libgcc_s.so is not an ELF
# but a GNU ld linker script (`GROUP(libgcc_s.so.1 -lgcc)`, the standard GCC
# layout), so install_data would bundle that text file where a shared library
# belongs -- and both the runtime loader and auditwheel then choke trying to
# read it as ELF. The real shared object is lib/libgcc_s.so.1; bundle that
# under both names instead (see the versioned-copy block below for the .so.1).
fs.copyfile('lib/libgcc_s.so.1', 'libgcc_s.so', install: true, install_dir: get_option('libdir'))

install_data('lib/libgfortran.so', install_dir: get_option('libdir'))

install_data('lib/libgomp.so', install_dir: get_option('libdir'))

install_data('lib/libstdc++.so', install_dir: get_option('libdir'))

# Each lib/lib*.so above is the unversioned dev-time name, but consumers need
# the versioned name matching the library's own DT_SONAME (the standard,
# long-stable soname for each of these). install_symlink() would be lighter,
# but its target is invisible to meson's own install-plan introspection,
# which meson-python relies on to decide what goes in the wheel, so it is
# silently dropped there; fs.copyfile() is a real, independently-tracked
# install target instead. libgcc_s.so.1 is sourced from the real ELF, not
# lib/libgcc_s.so (a linker script; see above).
fs.copyfile('lib/libatomic.so', 'libatomic.so.1', install: true, install_dir: get_option('libdir'))

fs.copyfile('lib/libgcc_s.so.1', 'libgcc_s.so.1', install: true, install_dir: get_option('libdir'))

fs.copyfile('lib/libgfortran.so', 'libgfortran.so.5', install: true, install_dir: get_option('libdir'))

fs.copyfile('lib/libgomp.so', 'libgomp.so.1', install: true, install_dir: get_option('libdir'))

fs.copyfile('lib/libstdc++.so', 'libstdc++.so.6', install: true, install_dir: get_option('libdir'))



compilersupportlibraries_dep = declare_dependency(
  include_directories: include_dirs,
  dependencies: [

    libatomic,

    libgcc_s,

    libgfortran,

    libgomp,

    libstdcxx,


  ],
)