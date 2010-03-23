
import os, copy
from distutils.cygwinccompiler import Mingw32CCompiler

class JCCMinGW32CCompiler(Mingw32CCompiler):

    def link(self, target_desc, objects, output_filename, output_dir=None,
             libraries=None, library_dirs=None, runtime_library_dirs=None,
             export_symbols=None, debug=0, extra_preargs=None,
             extra_postargs=None, build_temp=None, target_lang=None): 
 
        # use separate copies, so we can modify the lists
        extra_preargs = copy.copy(extra_preargs or [])

        (dll_name, dll_extension) = os.path.splitext(output_filename)
        if dll_extension.lower() == ".dll":
            extra_preargs.extend(["-Wl,--out-implib,%s" %(os.path.join(os.path.dirname(dll_name), "jcc", "jcc.lib"))])

        orig_Mingw32CCompiler.link(self, target_desc=target_desc,
                                   objects=objects,
                                   output_filename=output_filename, 
                                   output_dir=output_dir, libraries=libraries,
                                   library_dirs=library_dirs,
                                   runtime_library_dirs=runtime_library_dirs,
                                   export_symbols=export_symbols, debug=debug,
                                   extra_preargs=extra_preargs,
                                   extra_postargs=extra_postargs, 
                                   build_temp=build_temp,
                                   target_lang=target_lang)
