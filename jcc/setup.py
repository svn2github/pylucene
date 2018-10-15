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

import os, sys, platform, subprocess

jcc_ver = '3.3'
machine = platform.machine()
using_python2 = sys.version_info < (3,)

if not using_python2 and sys.version_info < (3, 3):
    raise RuntimeError('''
Python 3 is supported from version 3.3, you are running version %s.%s'''
                       %(sys.version_info.major, sys.version_info.minor))

if machine.startswith("iPod") or machine.startswith("iPhone"):
    platform = 'ipod'
elif sys.platform == "win32" and "--compiler=mingw32" in sys.argv:
    platform = 'mingw32'
elif sys.platform.startswith('linux'):
    platform = 'linux'
else:
    platform = sys.platform

# Add or edit the entry corresponding to your system in the JDK, INCLUDES,
# CFLAGS, DEBUG_CFLAGS, LFLAGS and JAVAC dictionaries below.
# These entries are used to build JCC _and_ by JCC to drive compiling and
# linking via distutils or setuptools the extensions it generated code for.
#
# The key for your system is determined by the platform variable defined
# above.
#
# Instead of editing the entries below, you may also override these
# dictionaries with JCC_JDK, JCC_INCLUDES, JCC_CFLAGS, JCC_DEBUG_CFLAGS,
# JCC_LFLAGS and JCC_JAVAC environment variables using os.pathsep as value
# separator.

if platform in ("win32", "mingw32"):
    try:
        JAVAFRAMEWORKS = None
        if using_python2:
            from helpers2.windows import JAVAHOME
        else:
            from helpers3.windows import JAVAHOME
    except ImportError:
        JAVAHOME = None
elif platform in ("darwin",):
    try:
        if using_python2:
            from helpers2.darwin import JAVAHOME, JAVAFRAMEWORKS
        else:
            from helpers3.darwin import JAVAHOME, JAVAFRAMEWORKS
    except ImportError:
        JAVAHOME = None
        JAVAFRAMEWORKS = None
else:
    JAVAHOME = None
    JAVAFRAMEWORKS = None

JDK = {
    'darwin': JAVAHOME or JAVAFRAMEWORKS,
    'ipod': '/usr/include/gcc',
    'linux': '/usr/lib/jvm/java-8-oracle',
    'sunos5': '/usr/jdk/instances/jdk1.6.0',
    'win32': JAVAHOME,
    'mingw32': JAVAHOME,
    'freebsd7': '/usr/local/diablo-jdk1.6.0'
}
if 'JCC_JDK' in os.environ:
    JDK[platform] = os.environ['JCC_JDK']


if not JDK[platform]:
    raise RuntimeError('''

Can't determine where the Java JDK has been installed on this machine.

Please set the environment variable JCC_JDK to that location before
running setup.py.
''')

elif not os.path.isdir(JDK[platform]):
    raise RuntimeError('''

Java JDK directory '%s' does not exist.

Please set the environment variable JCC_JDK to the correct location before
running setup.py.
''' %(JDK[platform]))


INCLUDES = {
    'darwin/frameworks': ['%(darwin)s/Headers' %(JDK)],
    'darwin/home': ['%(darwin)s/include' %(JDK),
                    '%(darwin)s/include/darwin' %(JDK)],
    'ipod': ['%(ipod)s/darwin/default' %(JDK)],
    'linux': ['%(linux)s/include' %(JDK),
              '%(linux)s/include/linux' %(JDK)],
    'sunos5': ['%(sunos5)s/include' %(JDK),
               '%(sunos5)s/include/solaris' %(JDK)],
    'win32': ['%(win32)s/include' %(JDK),
              '%(win32)s/include/win32' %(JDK)],
    'mingw32': ['%(mingw32)s/include' %(JDK),
                '%(mingw32)s/include/win32' %(JDK)],
    'freebsd7': ['%(freebsd7)s/include' %(JDK),
                 '%(freebsd7)s/include/freebsd' %(JDK)],
}

CFLAGS = {
    'darwin': ['-fno-strict-aliasing', '-Wno-write-strings',
               '-mmacosx-version-min=10.9', '-std=c++11', '-stdlib=libc++'],
    'ipod': ['-Wno-write-strings'],
    'linux': ['-fno-strict-aliasing', '-Wno-write-strings'],
    'sunos5': ['-features=iddollar',
               '-erroff=badargtypel2w,wbadinitl,wvarhidemem'],
    'win32': ["/EHsc", "/D_CRT_SECURE_NO_WARNINGS"],  # MSVC 9 (2008)
    'mingw32': ['-fno-strict-aliasing', '-Wno-write-strings'],
    'freebsd7': ['-fno-strict-aliasing', '-Wno-write-strings'],
}

# added to CFLAGS when JCC is invoked with --debug
DEBUG_CFLAGS = {
    'darwin': ['-O0', '-g', '-DDEBUG'],
    'ipod': ['-O0', '-g', '-DDEBUG'],
    'linux': ['-O0', '-g', '-DDEBUG'],
    'sunos5': ['-DDEBUG'],
    'win32': ['/Od', '/DDEBUG'],
    'mingw32': ['-O0', '-g', '-DDEBUG'],
    'freebsd7': ['-O0', '-g', '-DDEBUG'],
}

LFLAGS = {
    'darwin/frameworks': ['-framework', 'JavaVM', '-mmacosx-version-min=10.9'],
    'darwin/home': ['-L%(darwin)s/jre/lib' %(JDK), '-ljava',
                    '-L%(darwin)s/jre/lib/server' %(JDK), '-ljvm',
                    '-Wl,-rpath', '-Wl,%(darwin)s/jre/lib' %(JDK),
                    '-Wl,-rpath', '-Wl,%(darwin)s/jre/lib/server' %(JDK),
                    '-mmacosx-version-min=10.9'],
    'ipod': ['-ljvm', '-lpython%s.%s' %(sys.version_info[0:2]),
             '-L/usr/lib/gcc/arm-apple-darwin9/4.0.1'],
    'linux/i386': ['-L%(linux)s/jre/lib/i386' %(JDK), '-ljava',
                    '-L%(linux)s/jre/lib/i386/client' %(JDK), '-ljvm',
                    '-Wl,-rpath=%(linux)s/jre/lib/i386:%(linux)s/jre/lib/i386/client' %(JDK)],
    'linux/i686': ['-L%(linux)s/jre/lib/i386' %(JDK), '-ljava',
                    '-L%(linux)s/jre/lib/i386/client' %(JDK), '-ljvm',
                    '-Wl,-rpath=%(linux)s/jre/lib/i386:%(linux)s/jre/lib/i386/client' %(JDK)],
    'linux/x86_64': ['-L%(linux)s/jre/lib/amd64' %(JDK), '-ljava',
                      '-L%(linux)s/jre/lib/amd64/server' %(JDK), '-ljvm',
                      '-Wl,-rpath=%(linux)s/jre/lib/amd64:%(linux)s/jre/lib/amd64/server' %(JDK)],
    'sunos5': ['-L%(sunos5)s/jre/lib/i386' %(JDK), '-ljava',
               '-L%(sunos5)s/jre/lib/i386/client' %(JDK), '-ljvm',
               '-R%(sunos5)s/jre/lib/i386:%(sunos5)s/jre/lib/i386/client' %(JDK)],
    'win32': ['/DLL', '/LIBPATH:%(win32)s/lib' %(JDK), 'Ws2_32.lib', 'jvm.lib'],
    'mingw32': ['-L%(mingw32)s/lib' %(JDK), '-ljvm'],
    'freebsd7': ['-L%(freebsd7)s/jre/lib/i386' %(JDK), '-ljava', '-lverify',
                 '-L%(freebsd7)s/jre/lib/i386/client' %(JDK), '-ljvm',
                 '-Wl,-rpath=%(freebsd7)s/jre/lib/i386:%(freebsd7)s/jre/lib/i386/client' %(JDK)],
}

IMPLIB_LFLAGS = {
    'win32': ["/IMPLIB:%s"],
    'mingw32': ["-Wl,--out-implib,%s"]
}

if platform == 'linux':
    LFLAGS['linux'] = LFLAGS['linux/%s' %(machine)]
elif platform == 'darwin':
    if JAVAHOME is not None:
        INCLUDES['darwin'] = INCLUDES['darwin/home']
        LFLAGS['darwin'] = LFLAGS['darwin/home']
    elif JAVAFRAMEWORKS is not None:
        INCLUDES['darwin'] = INCLUDES['darwin/frameworks']
        LFLAGS['darwin'] = LFLAGS['darwin/frameworks']

JAVAC = {
    'darwin': ['javac', '-source', '1.5', '-target', '1.5'],
    'ipod': ['jikes', '-cp', '/usr/share/classpath/glibj.zip'],
    'linux': ['javac'],
    'sunos5': ['javac'],
    'win32': ['%(win32)s/bin/javac.exe' %(JDK)],
    'mingw32': ['%(mingw32)s/bin/javac.exe' %(JDK)],
    'freebsd7': ['javac'],
}

JAVADOC = {
    'darwin': ['javadoc'],
    'ipod': [],
    'linux': ['javadoc'],
    'sunos5': ['javadoc'],
    'win32': ['%(win32)s/bin/javadoc.exe' %(JDK)],
    'mingw32': ['%(mingw32)s/bin/javadoc.exe' %(JDK)],
    'freebsd7': ['javadoc'],
}

try:
    if 'USE_DISTUTILS' in os.environ:
        raise ImportError
    from setuptools import setup, Extension
    from pkg_resources import require
    with_setuptools = require('setuptools')[0].parsed_version

    try:
        from pkg_resources import SetuptoolsVersion
        with_modern_setuptools = True
    except ImportError:
        try:
            from pkg_resources.extern.packaging.version import Version
            with_modern_setuptools = True
        except ImportError:
            with_modern_setuptools = False

    enable_shared = False

    if with_modern_setuptools and 'NO_SHARED' not in os.environ:
        if platform in ('ipod', 'win32'):
            enable_shared = True

        elif platform == 'darwin':
            enable_shared = True

        elif platform == 'linux':
            if using_python2:
                from helpers2.linux import patch_setuptools
            else:
                from helpers3.linux import patch_setuptools
            enable_shared = patch_setuptools(with_setuptools)

        elif platform == 'mingw32':
            enable_shared = True
            # need to monkeypatch the CygwinCCompiler class to generate
            # jcc.lib in the correct place
            if using_python2:
                from helpers2.mingw32 import JCCMinGW32CCompiler
            else:
                from helpers3.mingw32 import JCCMinGW32CCompiler
            import distutils.cygwinccompiler
            distutils.cygwinccompiler.Mingw32CCompiler = JCCMinGW32CCompiler

        if enable_shared:
            from setuptools.extension import Library

except ImportError:
    if sys.version_info < (2, 4):
        raise ImportError('setuptools is required when using Python 2.3')
    else:
        from distutils.core import setup, Extension
        with_setuptools = None
        enable_shared = False


def main(debug):

    if using_python2:
        py_version_suffix = '2'
    else:
        py_version_suffix = '3'

    _jcc_argsep = os.environ.get('JCC_ARGSEP', os.pathsep)

    if 'JCC_INCLUDES' in os.environ:
        _includes = os.environ['JCC_INCLUDES'].split(_jcc_argsep)
    else:
        _includes = INCLUDES[platform]

    if 'JCC_CFLAGS' in os.environ:
        _cflags = os.environ['JCC_CFLAGS'].split(_jcc_argsep)
    else:
        _cflags = CFLAGS[platform]

    if 'JCC_DEBUG_CFLAGS' in os.environ:
        _debug_cflags = os.environ['JCC_DEBUG_CFLAGS'].split(_jcc_argsep)
    else:
        _debug_cflags = DEBUG_CFLAGS[platform]

    if 'JCC_LFLAGS' in os.environ:
        _lflags = os.environ['JCC_LFLAGS'].split(_jcc_argsep)
    else:
        _lflags = LFLAGS[platform]

    if 'JCC_IMPLIB_LFLAGS' in os.environ:
        _implib_lflags = os.environ['JCC_IMPLIB_LFLAGS'].split(_jcc_argsep)
    else:
        _implib_lflags = IMPLIB_LFLAGS.get(platform, [])

    if 'JCC_JAVAC' in os.environ:
        _javac = os.environ['JCC_JAVAC'].split(_jcc_argsep)
    else:
        _javac = JAVAC[platform]

    if 'JCC_JAVADOC' in os.environ:
        _javadoc = os.environ['JCC_JAVADOC'].split(_jcc_argsep)
    else:
        _javadoc = JAVADOC[platform]

    if using_python2:
        from helpers2.build import jcc_build_py
    else:
        from helpers3.build import jcc_build_py

    jcc_build_py.config_file = \
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     'jcc%s' %(py_version_suffix), 'config.py')
    jcc_build_py.config_text = \
        '\n'.join(['',
                   'INCLUDES=%s' %(_includes),
                   'CFLAGS=%s' %(_cflags),
                   'DEBUG_CFLAGS=%s' %(_debug_cflags),
                   'LFLAGS=%s' %(_lflags),
                   'IMPLIB_LFLAGS=%s' %(_implib_lflags),
                   'SHARED=%s' %(enable_shared),
                   'VERSION="%s"' %(jcc_ver),
                   ''])

    extensions = []

    boot = '_jcc%s' %(py_version_suffix)

    cflags = ['-DPYTHON'] + _cflags
    if debug:
        cflags += _debug_cflags
    includes = _includes + [boot, 'jcc%s/sources' %(py_version_suffix)]
    lflags = _lflags
    if not debug:
        if platform == 'win32':
            pass
        elif platform == 'sunos5':
            lflags += ['-Wl,-s']
        else:
            lflags += ['-Wl,-S']

    sources = ['jcc%s/sources/jcc.cpp' %(py_version_suffix),
               'jcc%s/sources/JCCEnv.cpp' %(py_version_suffix),
               'jcc%s/sources/JObject.cpp' %(py_version_suffix),
               'jcc%s/sources/JArray.cpp' %(py_version_suffix),
               'jcc%s/sources/functions.cpp' %(py_version_suffix),
               'jcc%s/sources/types.cpp' %(py_version_suffix)]
    for path, dirs, names in os.walk(boot):
        for name in names:
            if name.endswith('.cpp'):
                sources.append(os.path.join(path, name))
    package_data = ['sources/*.cpp', 'sources/*.h', 'patches/patch.*']

    if with_setuptools and enable_shared:
        from subprocess import Popen, PIPE

        kwds = { "extra_compile_args": cflags,
                 "include_dirs": includes,
                 "define_macros": [('_jcc_lib', None),
                                   ('JCC_VER', '"%s"' %(jcc_ver))],
                 "sources": sources[0:2] }

        if platform in ('darwin', 'ipod'):
            kwds["extra_link_args"] = \
                lflags + ['-install_name',
                          '@rpath/libjcc%s.dylib' %(py_version_suffix),
                          '-current_version', jcc_ver,
                          '-compatibility_version', jcc_ver]
        elif platform == 'linux':
            kwds["extra_link_args"] = \
                lflags + ['-lpython%s.%s%s' %(
                    sys.version_info[0:2] + ('' if using_python2 else 'm',))]
            kwds["force_shared"] = True    # requires jcc/patches/patch.43
        elif platform in IMPLIB_LFLAGS:
            jcclib = 'jcc%s%s.lib' %(py_version_suffix, debug and '_d' or '')
            implib_flags = ' '.join(IMPLIB_LFLAGS[platform])
            kwds["extra_link_args"] = \
                lflags + [implib_flags %(os.path.join('jcc%s' %(py_version_suffix), jcclib))]
            package_data.append(jcclib)
        else:
            kwds["extra_link_args"] = lflags

        extensions.append(Library('jcc%s' %(py_version_suffix), **kwds))

        args = _javac[:]
        args.extend(('-d', 'jcc%s/classes' %(py_version_suffix)))
        args.append('java/org/apache/jcc/PythonVM.java')
        args.append('java/org/apache/jcc/PythonException.java')
        if not os.path.exists('jcc%s/classes' %(py_version_suffix)):
            os.makedirs('jcc%s/classes' %(py_version_suffix))
        try:
            process = Popen(args, stderr=PIPE)
        except:
            raise sys.exc_info()[0]("%s: %s" %(sys.exc_info()[1], args))
        process.wait()
        if process.returncode != 0:
            raise OSError(process.stderr.read())
        package_data.append('classes/org/apache/jcc/PythonVM.class')
        package_data.append('classes/org/apache/jcc/PythonException.class')

        args = _javadoc[:]
        args.extend(('-d', 'javadoc', '-sourcepath', 'java', 'org.apache.jcc'))
        try:
            process = Popen(args, stderr=PIPE)
        except:
            raise sys.exc_info()[0]("%s: %s" %(sys.exc_info()[1], args))
        process.wait()
        if process.returncode != 0:
            raise OSError(process.stderr.read())

    extensions.append(Extension('jcc._jcc%s' %(py_version_suffix),
                                extra_compile_args=cflags,
                                extra_link_args=lflags,
                                include_dirs=includes,
                                define_macros=[('_java_generics', None),
                                               ('JCC_VER', '"%s"' %(jcc_ver))],
                                sources=sources))

    args = {
        'name': 'JCC',
        'version': jcc_ver,
        'description': 'a C++ code generator for calling Java from C++/Python',
        'long_description': open('DESCRIPTION').read(),
        'author': 'Andi Vajda',
        'author_email': 'vajda@apache.org',
        'classifiers': ['Development Status :: 5 - Production/Stable',
                        'Environment :: Console',
                        'Intended Audience :: Developers',
                        'License :: OSI Approved :: Apache Software License',
                        'Operating System :: OS Independent',
                        'Programming Language :: C++',
                        'Programming Language :: Java',
                        'Programming Language :: Python',
                        'Programming Language :: Python :: 2',
                        'Programming Language :: Python :: 3',
                        'Programming Language :: Python :: Implementation :: CPython',
                        'Topic :: Software Development :: Code Generators',
                        'Topic :: Software Development :: Libraries :: Java Libraries'],
        'packages': ['jcc'],
        'package_dir': {'jcc': 'jcc%s' %(py_version_suffix)},
        'package_data': {'jcc': package_data},
        'ext_modules': extensions,
        "cmdclass": {"build_py": jcc_build_py},
    }
    if with_setuptools:
        args['zip_safe'] = False

    setup(**args)


if __name__ == "__main__":
    main('--debug' in sys.argv)
