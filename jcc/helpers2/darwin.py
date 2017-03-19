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

import sys, os

global JAVAHOME, JAVAFRAMEWORKS
JAVAHOME = None
JAVAFRAMEWORKS = None

if sys.platform == "darwin":

    # figure out where the JDK lives
    from subprocess import Popen, PIPE

    try:
        args = ['/usr/libexec/java_home']
        process = Popen(args, stdout=PIPE, stderr=PIPE)
    except Exception, e:
        print >>sys.stderr, "%s: %s" %(e, args)
    else:
        process.wait()
        if process.returncode == 0:
            _path = process.stdout.read().strip()
            if os.path.exists(os.path.join(_path, "include", "jni.h")):
                JAVAHOME = _path
                print >>sys.stderr, 'found JAVAHOME =', JAVAHOME
        else:
            print >>sys.stderr, process.stderr.read()

    # figure out where the JDK Frameworks lives
    import platform, re
    _os_version = re.match("[0-9]+\.[0-9]+", platform.mac_ver()[0]).group(0)

    # this is where Apple says we should look for headers
    _path = "/System/Library/Frameworks/JavaVM.framework"
    if os.path.exists(os.path.join(_path, "Headers", "jni.h")):
        JAVAFRAMEWORKS = _path
        print >>sys.stderr, 'found JAVAFRAMEWORKS =', JAVAFRAMEWORKS
    else:
        # but their updates don't always match their documentation, 
        # so look up the same path in the OS's /Developer tree
        _path = "/Developer/SDKs/MacOSX%s.sdk%s" %(_os_version, _path)
        if os.path.exists(os.path.join(_path, "Headers", "jni.h")):
            JAVAFRAMEWORKS = _path
            print >>sys.stderr, 'found JAVAFRAMEWORKS =', JAVAFRAMEWORKS

    # monkeypatch customize_compiler so that we can remove -Wl,-x from LDSHARED
    # set in setuptools.command.build_ext.build_ext.setup_shlib_compiler
    from distutils.sysconfig import customize_compiler, get_config_vars

    def _customize_compiler(compiler):
        get_config_vars()['LDSHARED'] = "gcc -dynamiclib -undefined dynamic_lookup"
        customize_compiler(compiler)

    from distutils import sysconfig
    sysconfig.customize_compiler = _customize_compiler
