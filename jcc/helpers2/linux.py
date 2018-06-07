#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sys, os, os.path, re
import distutils, setuptools

from setuptools import dist, extension
from setuptools.command import build_ext
from setuptools.extension import Library as _Library


def patch_st_dir(patch_version, st_egg, jccdir):
    return '''

Shared mode is disabled, setuptools patch.43.%s must be applied to enable it
or the NO_SHARED environment variable must be set to turn off this error.

    sudo patch -d %s -Nup0 < %s/jcc2/patches/patch.43.%s

See %s/INSTALL for more information about shared mode.
''' %(patch_version, st_egg, jccdir, patch_version, jccdir)


def patch_st_zip(patch_version, st_egg, jccdir):
    return '''

Shared mode is disabled, setuptools patch.43.%s must be applied to enable it
or the NO_SHARED environment variable must be set to turn off this error.

    mkdir tmp
    cd tmp
    unzip -q %s
    patch -Nup0 < %s/jcc2/patches/patch.43.%s
    sudo zip %s -f
    cd ..
    rm -rf tmp

See %s/INSTALL for more information about shared mode.
''' %(patch_version, st_egg, jccdir, patch_version, st_egg, jccdir)



def patch_setuptools(with_setuptools):

    try:
        from setuptools.command.build_ext import sh_link_shared_object
        enable_shared = True  # jcc2/patches/patch.43 was applied
    except ImportError:
        jccdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        st_egg = os.path.dirname(setuptools.__path__[0])
            
        setuptools.Library = LinuxLibrary
        extension.Library = LinuxLibrary
        build_ext.build_ext = LinuxBuildExt
        if build_ext.use_stubs:
            # Build shared libraries.
            global sh_link_shared_object # Fix UnboundLocalError
            build_ext.link_shared_object = sh_link_shared_object
        else:
            # Build static libraries every where else (unless forced)
            build_ext.libtype = 'static'
            build_ext.link_shared_object = st_link_shared_object
                
        print >>sys.stderr, "Applied shared mode monkey patch to:", setuptools
        return True # monkey patch was applied

    return enable_shared


class LinuxLibrary(_Library):
    def __init__(self, *args, **kwds):
        self.force_shared = kwds.pop('force_shared', False)
        extension.Extension.__init__(self, *args, **kwds)


class LinuxBuildExt(build_ext.build_ext):

    def get_ext_filename(self, fullname):
        filename = build_ext._build_ext.get_ext_filename(self, fullname)
        if fullname in self.ext_map:
            ext = self.ext_map[fullname]
            if isinstance(ext, _Library):
                if ext.force_shared and not build_ext.use_stubs:
                    libtype = 'shared'
                else:
                    libtype = build_ext.libtype
                fn, ext = os.path.splitext(filename)
                return self.shlib_compiler.library_filename(fn, libtype)
            elif build_ext.use_stubs and ext._links_to_dynamic:
                d, fn = os.path.split(filename)
                return os.path.join(d, 'dl-' + fn)
        return filename

    def build_extension(self, ext):
        _compiler = self.compiler
        try:
            force_shared = False
            if isinstance(ext, _Library):
                self.compiler = self.shlib_compiler
                force_shared = ext.force_shared and not build_ext.use_stubs
                if force_shared:
                    self.compiler.link_shared_object = sh_link_shared_object.__get__(self.compiler)
            build_ext._build_ext.build_extension(self, ext)
            if ext._needs_stub:
                self.write_stub(self.get_finalized_command('build_py').build_lib, ext)
        finally:
            if force_shared:
                self.compiler.link_shared_object = build_ext.link_shared_object.__get__(self.compiler)
            self.compiler = _compiler


def sh_link_shared_object(self, objects, output_libname, output_dir=None, libraries=None, library_dirs=None, runtime_library_dirs=None, export_symbols=None, debug=0, extra_preargs=None, extra_postargs=None, build_temp=None, target_lang=None):
    self.link(self.SHARED_LIBRARY, objects, output_libname, output_dir, libraries, library_dirs, runtime_library_dirs, export_symbols, debug, extra_preargs, extra_postargs, build_temp, target_lang)

def st_link_shared_object(self, objects, output_libname, output_dir=None, libraries=None, library_dirs=None, runtime_library_dirs=None, export_symbols=None, debug=0, extra_preargs=None, extra_postargs=None, build_temp=None, target_lang=None):
    assert output_dir is None   # distutils build_ext doesn't pass this
    output_dir, filename = os.path.split(output_libname)
    basename, ext = os.path.splitext(filename)
    if self.library_filename("x").startswith('lib'):
        # strip 'lib' prefix; this is kludgy if some platform uses
        # a different prefix
        basename = basename[3:]

    self.create_static_lib(objects, basename, output_dir, debug, target_lang)
