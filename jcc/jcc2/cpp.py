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

import os, sys, zipfile, _jcc2

python_ver = '%d.%d.%d' %(sys.version_info[0:3])
if python_ver < '2.4':
    from sets import Set as set

    def split_pkg(string, sep):
        parts = string.split(sep)
        if len(parts) > 1:
            return sep.join(parts[:-1]), parts[-1]
        return parts

    def sort(list, fn=None, key=None):
        if fn:
            list.sort(fn)
        elif key:
            def fn(x, y):
                return cmp(key(x), key(y))
            list.sort(fn)
        else:
            list.sort()

else:
    def split_pkg(string, sep):
        return string.rsplit(sep, 1)

    def sort(list, fn=None, key=None):
        if fn:
            list.sort(cmp=fn)
        elif key:
            list.sort(key=key)
        else:
            list.sort()


class JavaError(Exception):

    def getJavaException(self):
        return self.args[0]

    def __str__(self):
        writer = StringWriter()
        self.getJavaException().printStackTrace(PrintWriter(writer))

        return '\n'.join((super(JavaError, self).__str__(),
                          "Java stacktrace:", str(writer)))


class InvalidArgsError(Exception):
    pass


_jcc2._set_exception_types(JavaError, InvalidArgsError)
from _jcc2 import findClass as _findClass
from _jcc2 import *


def findClass(className):

    try:
        cls = _findClass(className)
    except:
        print >>sys.stderr, "While loading", className
        raise

    if cls is None:
        raise ValueError, className

    return cls


INDENT = '  '
HALF_INDENT = ' '

PRIMITIVES = { 'boolean': 'Z',
               'byte': 'B',
               'char': 'C',
               'double': 'D',
               'float': 'F',
               'int': 'I',
               'long': 'J',
               'short': 'S',
               'void': 'V' }

RESERVED = set(['delete', 'and', 'or', 'not', 'xor', 'union', 'register',
                'const', 'bool', 'operator', 'typeof', 'asm', 'mutable',
                'inline', 'typedef', 'struct', 'extern',
                'NULL', 'DOMAIN', 'IGNORE', 'min', 'max', 'PREFIX'])

RENAME_METHOD_SUFFIX = '_'
RENAME_FIELD_SUFFIX = '__'

def cppname(name):

    if name in RESERVED:
        return name + '$'

    return name


def cppnames(names):

    return [cppname(name) for name in names]


def absname(names):

    if names:
        return "::%s" %('::'.join(names))

    return ''


def typename(cls, current, const):

    if cls.isArray():
        componentType = cls.getComponentType()
        name = 'JArray< %s >' %(typename(componentType, current, False))

    elif cls.isPrimitive():
        name = cls.getName()
        if name != 'void':
            name = 'j' + name
        const = False

    elif cls == current:
        name = cppname(cls.getName().split('.')[-1])

    else:
        name = absname([cppname(name) for name in cls.getName().split('.')])

    if const:
        return "const %s &" %(name)

    return name


def argnames(params, cls):

    if not params:
        return '', ''

    count = len(params)
    decls = ', '.join(["%s a%d" %(typename(params[i], cls, True), i)
                       for i in xrange(count)])
    args = ', '.join(['a%d%s' %(i, not params[i].isPrimitive() and '.this$' or '')
                      for i in xrange(count)])

    return decls, ', ' + args


def line(out, indent=0, string='', *args):

    out.write(INDENT * indent)
    out.write(string % args)
    out.write('\n')


def known(cls, typeset, declares, packages, excludes, generics):

    if generics:
        if Class.instance_(cls):
            cls = Class.cast_(cls)
        elif ParameterizedType.instance_(cls):
            pt = ParameterizedType.cast_(cls)
            if not known(pt.getRawType(), typeset, declares, packages, excludes,
                         True):
                return False
            for ta in pt.getActualTypeArguments():
                if TypeVariable.instance_(ta):
                    continue
                if not known(ta, typeset, declares, packages, excludes, True):
                    return False
            return True
        elif WildcardType.instance_(cls):
            wc = WildcardType.cast_(cls)
            for ub in wc.getUpperBounds():
                if not known(ub, typeset, declares, packages, excludes, True):
                    return False
            return True
        elif TypeVariable.instance_(cls):
            for bounds in TypeVariable.cast_(cls).getBounds():
                if not known(bounds, typeset, declares, packages, excludes,
                             True):
                    return False
            return True
        elif GenericArrayType.instance_(cls):
            return known(GenericArrayType.cast_(cls).getGenericComponentType(),
                         typeset, declares, packages, excludes, True)
        else:
            raise TypeError, (cls, cls.getClass())

    while cls.isArray():
        cls = cls.getComponentType()

    className = cls.getName()
    if className.split('$', 1)[0] in excludes or className in excludes:
        return False

    if cls.isPrimitive():
        return True

    if cls in typeset:
        declares.add(cls)
        return True

    if split_pkg(className, '.')[0] in packages:
        typeset.add(cls)
        declares.add(cls)
        cls = cls.getSuperclass()
        while cls and cls not in typeset:
            typeset.add(cls)
            cls = cls.getSuperclass()
        return True

    return False


def addRequiredTypes(cls, typeset, generics):

    if generics:
        if Class.instance_(cls):
            cls = Class.cast_(cls)
            if not (cls.isPrimitive() or cls in typeset):
                if cls.isArray():
                    addRequiredTypes(cls.getComponentType(), typeset, True)
                else:
                    typeset.add(cls)
                    cls = cls.getGenericSuperclass()
                    if cls is not None:
                        addRequiredTypes(cls, typeset, True)
        elif ParameterizedType.instance_(cls):
            pt = ParameterizedType.cast_(cls)
            addRequiredTypes(pt.getRawType(), typeset, True)
            for ta in pt.getActualTypeArguments():
                addRequiredTypes(ta, typeset, True)
        elif GenericArrayType.instance_(cls):
            gat = GenericArrayType.cast_(cls)
            addRequiredTypes(gat.getGenericComponentType(), typeset, True)
        elif not (TypeVariable.instance_(cls) or WildcardType.instance_(cls)):
            raise NotImplementedError, repr(cls)
    else:
        if cls not in typeset:
            typeset.add(cls)
            cls = cls.getSuperclass()
            if cls is not None:
                addRequiredTypes(cls, typeset, False)


def getActualTypeArguments(pt):

    while True:
        arguments = pt.getActualTypeArguments()
        if arguments:
            return arguments
        pt = pt.getOwnerType()
        if pt is None or not ParameterizedType.instance_(pt):
            return []
        pt = ParameterizedType.cast_(pt)


def getTypeParameters(cls):
    if cls is None:
        return []

    parameters = cls.getTypeParameters()
    if parameters:
        return parameters

    superCls = cls.getGenericSuperclass()
    if Class.instance_(superCls):
        parameters = getTypeParameters(Class.cast_(superCls))
        if parameters:
            return parameters
    elif ParameterizedType.instance_(superCls):
        parameters = getActualTypeArguments(ParameterizedType.cast_(superCls))
        if parameters:
            return parameters

    parameters = getTypeParameters(cls.getDeclaringClass())
    if parameters:
        return parameters

    return []


def find_method(cls, name, params):

    declared = False
    while True:
        try:
            if declared:
                method = cls.getDeclaredMethod(name, params)
            else:
                method = cls.getMethod(name, params)
            break
        except JavaError, e:
            if (e.getJavaException().getClass().getName() == 'java.lang.NoSuchMethodException'):
                if not declared:
                    declared = True
                else:
                    cls = cls.getSuperclass()
                    if not cls:
                        return None
                continue
            raise

    modifiers = method.getModifiers()
    if Modifier.isAbstract(modifiers):
        return None
    if Modifier.isPrivate(modifiers):
        return None

    return method


def signature(fn, argsOnly=False):

    def typename(cls):
        array = ''
        while cls.isArray():
            array += '['
            cls = cls.getComponentType()
        if cls.isPrimitive():
            return array + PRIMITIVES[cls.getName()]
        return '%sL%s;' %(array, cls.getName().replace('.', '/'))
        
    if isinstance(fn, Constructor):
        returnType = 'V'
    elif isinstance(fn, Method):
        returnType = typename(fn.getReturnType())
    elif isinstance(fn, Field):
        return typename(fn.getType())

    if argsOnly:
        return '(%s)' %(''.join([typename(param)
                                 for param in fn.getParameterTypes()]))

    return '(%s)%s' %(''.join([typename(param)
                               for param in fn.getParameterTypes()]),
                       returnType)


def forward(out, namespace, indent):

    for name, entries in namespace.iteritems():
        if entries is True:
            line(out, indent, 'class %s;', cppname(name))
        else:
            line(out, indent, 'namespace %s {', cppname(name))
            forward(out, entries, indent + 1)
            line(out, indent, '}')


def expandjar(path):

    jar = zipfile.ZipFile(path, 'r')

    for member in jar.infolist():
        f = member.filename
        if not f.startswith('META-INF/') and f.endswith('.class'):
            yield f.split('.')[0].replace('/', '.')

    jar.close()


def jcc(args):

    classNames = set()
    listedClassNames = set()
    listedMethodOrFieldNames = {}
    packages = set()
    jars = []
    classpath = [_jcc2.CLASSPATH]
    libpath = []
    vmargs = ['-Djava.awt.headless=true']
    moduleName = None
    modules = []
    build = False
    install = False
    recompile = False
    egg_info = False
    output = 'build'
    debug = False
    excludes = []
    version = ''
    mappings = {}
    sequences = {}
    renames = {}
    use_full_names = False
    env = None
    wrapperFiles = 1
    prefix = None
    root = None
    install_dir = None
    home_dir = None
    use_distutils = False
    shared = False
    dist = False
    wininst = False
    find_jvm_dll = False
    compiler = None
    generics = hasattr(_jcc2, "Type")
    arch = []
    resources = []
    imports = {}
    extra_setup_args = []
    initvm_args = {}

    i = 1
    while i < len(args):
        arg = args[i]
        if arg.startswith('-'):
            if arg == '--jar':
                i += 1
                classpath.append(args[i])
                classNames.update(expandjar(args[i]))
                jars.append(args[i])
            elif arg == '--include':
                i += 1
                classpath.append(args[i])
                jars.append(args[i])
            elif arg == '--package':
                i += 1
                packages.add(args[i])
            elif arg == '--classpath':
                i += 1
                classpath.append(args[i])
            elif arg == '--libpath':
                i += 1
                libpath.append(args[i])
            elif arg == '--vmarg':
                i += 1
                vmargs.append(args[i])
            elif arg == '--maxheap':
                i += 1
                initvm_args['maxheap'] = args[i]
            elif arg == '--python':
                from python import python, module
                i += 1
                moduleName = args[i]
            elif arg == '--module':
                i += 1
                modules.append(args[i])
            elif arg == '--build':
                from python import compile
                build = True
            elif arg == '--install':
                from python import compile
                install = True
            elif arg == '--compile':
                from python import compile
                recompile = True
            elif arg == '--egg-info':
                from python import compile
                egg_info = True
            elif arg == '--extra-setup-arg':
                i += 1
                extra_setup_args.append(args[i])
            elif arg == '--output':
                i += 1
                output = args[i]
            elif arg == '--debug':
                debug = True
            elif arg == '--exclude':
                i += 1
                excludes.append(args[i])
            elif arg == '--version':
                i += 1
                version = args[i]
            elif arg == '--mapping':
                mappings[args[i + 1]] = args[i + 2]
                i += 2
            elif arg == '--sequence':
                sequences[args[i + 1]] = (args[i + 2], args[i + 3])
                i += 3
            elif arg == '--rename':
                i += 1
                renames.update(dict([arg.split('=')
                                     for arg in args[i].split(',')]))
            elif arg == '--use_full_names':
                use_full_names = True
            elif arg == '--files':
                i += 1
                wrapperFiles = args[i]
                if wrapperFiles != 'separate':
                    wrapperFiles = int(wrapperFiles)
            elif arg == '--prefix':
                i += 1
                prefix = args[i]
            elif arg == '--root':
                i += 1
                root = args[i]
            elif arg == '--install-dir':
                i += 1
                install_dir = args[i]
            elif arg == '--home':
                i += 1
                home_dir = args[i]
            elif arg == '--use-distutils':
                use_distutils = True
            elif arg == '--shared':
                shared = True
            elif arg == '--bdist':
                from python import compile
                dist = True
            elif arg == '--wininst':
                from python import compile
                wininst = True
                dist = True
            elif arg == '--compiler':
                i += 1
                compiler = args[i]
            elif arg == '--reserved':
                i += 1
                RESERVED.update(args[i].split(','))
            elif arg == '--arch':
                i += 1
                arch.append(args[i])
            elif arg == '--no-generics':
                generics = False
            elif arg == '--find-jvm-dll':
                find_jvm_dll = True
            elif arg == '--resources':
                i += 1
                resources.append(args[i])
            elif arg == '--import':
                i += 1
                imports[args[i]] = ()
            else:
                raise ValueError, "Invalid argument: %s" %(arg)
        else:
            if ':' in arg:
                arg, method = arg.split(':', 1)
                listedMethodOrFieldNames.setdefault(arg, set()).add(method)
            classNames.add(arg)
            listedClassNames.add(arg)
        i += 1

    if libpath:
        vmargs.append('-Djava.library.path=' + os.pathsep.join(libpath))

    initvm_args['maxstack'] = '512k'
    initvm_args['vmargs'] = vmargs

    env = initVM(os.pathsep.join(classpath) or None, **initvm_args)

    typeset = set()
    excludes = set(excludes)

    if imports:
        if shared:
            imports = dict((__import__(import_), set()) for import_ in imports)
        else:
            raise ValueError, "--shared must be used when using --import"

    if recompile or not build and (install or dist or egg_info):
        if moduleName is None:
            raise ValueError, 'module name not specified (use --python)'
        else:
            compile(env, os.path.dirname(args[0]), output, moduleName,
                    install, dist, debug, jars, version,
                    prefix, root, install_dir, home_dir, use_distutils,
                    shared, compiler, modules, wininst, find_jvm_dll,
                    arch, generics, resources, imports, use_full_names,
                    egg_info, extra_setup_args)
    else:
        if imports:
            def walk((include, importset), dirname, names):
                for name in names:
                    if name.endswith('.h'):
                        className = os.path.join(dirname[len(include) + 1:],
                                                 name[:-2])
                        if os.path.sep != '/':
                            className = className.replace(os.path.sep, '/')
                        importset.add(findClass(className))
            for import_, importset in imports.iteritems():
                env._addClassPath(import_.CLASSPATH)
                include = os.path.join(import_.__dir__, 'include')
                os.path.walk(include, walk, (include, importset))
                typeset.update(importset)
        typeset.add(findClass('java/lang/Object'))
        typeset.add(findClass('java/lang/Class'))
        typeset.add(findClass('java/lang/String'))
        typeset.add(findClass('java/lang/Throwable'))
        typeset.add(findClass('java/lang/Exception'))
        typeset.add(findClass('java/lang/RuntimeException'))
        if moduleName:
            typeset.add(findClass('java/lang/Number'))
            typeset.add(findClass('java/lang/Boolean'))
            typeset.add(findClass('java/lang/Byte'))
            typeset.add(findClass('java/lang/Character'))
            typeset.add(findClass('java/lang/Double'))
            typeset.add(findClass('java/lang/Float'))
            typeset.add(findClass('java/lang/Integer'))
            typeset.add(findClass('java/lang/Long'))
            typeset.add(findClass('java/lang/Short'))
            typeset.add(findClass('java/util/Iterator'))
            typeset.add(findClass('java/util/Enumeration'))
            typeset.add(findClass('java/io/StringWriter'))
            typeset.add(findClass('java/io/PrintWriter'))
            typeset.add(findClass('java/io/Writer'))
            packages.add('java.lang')

        for className in classNames:
            if className.split('$', 1)[0] in excludes or className in excludes:
                continue
            cls = findClass(className.replace('.', '/'))
            if (Modifier.isPublic(cls.getModifiers()) or
                className in listedClassNames):
                addRequiredTypes(cls, typeset, generics)

        _dll_export = ''
        if moduleName:
            cppdir = os.path.join(output, '_%s' %(moduleName))
            if shared and sys.platform == 'win32':
                _dll_export = "_dll_%s " %(moduleName)
        else:
            cppdir = output

        allInOne = wrapperFiles != 'separate'
        if allInOne:
            if not os.path.isdir(cppdir):
                os.makedirs(cppdir)
            if wrapperFiles <= 1:
                out_cpp = file(os.path.join(cppdir, '__wrap__.cpp'), 'w')
            else:
                fileCount = 1
                fileName = '__wrap%02d__.cpp' %(fileCount)
                out_cpp = file(os.path.join(cppdir, fileName), 'w')

        done = set()
        pythonNames = {}
        for importset in imports.itervalues():
            done.update(importset)
            if moduleName:
                for cls in importset:
                    name = split_pkg(cls.getName(), '.')[-1]
                    if not use_full_names:
                        if name in pythonNames:
                            raise ValueError, (cls, 'python class name already in use, use --rename', name, pythonNames[name])
                        else:
                            pythonNames[name] = cls

        todo = typeset - done
        if allInOne and wrapperFiles > 1:
            classesPerFile = max(1, len(todo) / wrapperFiles)
        classCount = 0
        while todo:
            for cls in todo:
                classCount += 1
                className = cls.getName()
                names = className.split('.')
                dir = os.path.join(cppdir, *names[:-1])
                if not os.path.isdir(dir):
                    os.makedirs(dir)

                fileName = os.path.join(dir, names[-1])
                out_h = file(fileName + '.h', "w")
                line(out_h, 0, '#ifndef %s_H', '_'.join(names))
                line(out_h, 0, '#define %s_H', '_'.join(names))

                (superCls, constructors, methods, protectedMethods,
                 methodNames, fields, instanceFields, declares) = \
                    header(env, out_h, cls, typeset, packages, excludes,
                           generics,
                           listedMethodOrFieldNames.get(cls.getName(), ()),
                           _dll_export)

                if not allInOne:
                    out_cpp = file(fileName + '.cpp', 'w')
                names, superNames = code(env, out_cpp,
                                         cls, superCls, constructors,
                                         methods, protectedMethods,
                                         methodNames, fields, instanceFields,
                                         declares, typeset)
                if moduleName:
                    name = renames.get(className) or names[-1]
                    if not use_full_names:
                        if name in pythonNames:
                            raise ValueError, (cls, 'python class name already in use, use --rename', name, pythonNames[name])
                        else:
                            pythonNames[name] = cls
                    python(env, out_h, out_cpp,
                           cls, superCls, names, superNames,
                           constructors, methods, protectedMethods,
                           methodNames, fields, instanceFields,
                           mappings.get(className), sequences.get(className),
                           renames.get(className),
                           declares, typeset, moduleName, generics,
                           _dll_export)

                line(out_h)
                line(out_h, 0, '#endif')
                out_h.close()

                if not allInOne:
                    out_cpp.close()
                elif wrapperFiles > 1:
                    if classCount >= classesPerFile:
                        out_cpp.close()
                        fileCount += 1
                        fileName = '__wrap%02d__.cpp' %(fileCount)
                        out_cpp = file(os.path.join(cppdir, fileName), 'w')
                        classCount = 0
                        
            done.update(todo)
            todo = typeset - done

        if allInOne:
            out_cpp.close()

        if moduleName:
            out = file(os.path.join(cppdir, moduleName) + '.cpp', 'w')
            module(out, allInOne, done, imports, cppdir, moduleName,
                   shared, generics, use_full_names)
            out.close()
            if build or install or dist or egg_info:
                compile(env, os.path.dirname(args[0]), output, moduleName,
                        install, dist, debug, jars, version,
                        prefix, root, install_dir, home_dir, use_distutils,
                        shared, compiler, modules, wininst, find_jvm_dll,
                        arch, generics, resources, imports, use_full_names,
                        egg_info, extra_setup_args)


def header(env, out, cls, typeset, packages, excludes, generics,
           listedMethodOrFieldNames, _dll_export):

    names = cls.getName().split('.')
    superCls = cls.getSuperclass()
    declares = set([cls.getClass()])

    interfaces = []
    if generics:
        for interface in cls.getGenericInterfaces():
            if Class.instance_(interface):
                pt = None
                interface = Class.cast_(interface)
            elif ParameterizedType.instance_(interface):
                pt = ParameterizedType.cast_(interface)
                interface = Class.cast_(pt.getRawType())
            else:
                raise NotImplementedError, repr(interface)
            if superCls and interface.isAssignableFrom(superCls):
                continue
            if known(interface, typeset, declares, packages, excludes, False):
                interfaces.append(interface)
                if pt is not None:
                    for ta in pt.getActualTypeArguments():
                        addRequiredTypes(ta, typeset, True)
    else:
        for interface in cls.getInterfaces():
            if superCls and interface.isAssignableFrom(superCls):
                continue
            if known(interface, typeset, declares, packages, excludes, False):
                interfaces.append(interface)

    if cls.isInterface():
        if interfaces:
            superCls = interfaces.pop(0)
        else:
            superCls = findClass('java/lang/Object')
        superClsName = superCls.getName()
    elif superCls:
        superClsName = superCls.getName()
        if generics:
            for clsParam in getTypeParameters(cls):
                if Class.instance_(clsParam):
                    addRequiredTypes(clsParam, typeset, True)
                    known(clsParam, typeset, declares, packages, excludes, True)
    else:
        superClsName = 'JObject'

    constructors = []
    for constructor in cls.getDeclaredConstructors():
        if Modifier.isPublic(constructor.getModifiers()):
            if generics:
                genericParams = constructor.getGenericParameterTypes()
                params = constructor.getParameterTypes()
                # It appears that the implicit instance-of-the-declaring-class
                # parameter of a non-static inner class is missing from 
                # getGenericParameterTypes()
                if len(params) == len(genericParams) + 1:
                    params[1:] = genericParams
                else:
                    params = genericParams
                if len(params) == 1:
                    if params[0] == cls:
                        continue
                    if ParameterizedType.instance_(params[0]):
                        param = ParameterizedType.cast_(params[0])
                        if param.getRawType() == cls:
                            continue
            else:
                params = constructor.getParameterTypes()
                if len(params) == 1 and params[0] == cls:
                    continue
            for param in params:
                if not known(param, typeset, declares, packages, excludes,
                             generics):
                    break
            else:
                constructors.append(constructor)
    sort(constructors, key=lambda x: len(x.getParameterTypes()))

    methods = {}
    protectedMethods = []
    for method in cls.getDeclaredMethods():
        if method.isSynthetic():
            continue
        modifiers = method.getModifiers()
        if (Modifier.isPublic(modifiers) or
            method.getName() in listedMethodOrFieldNames):
            if generics:
                returnType = method.getGenericReturnType()
            else:
                returnType = method.getReturnType()
            if not known(returnType, typeset, declares, packages, excludes,
                         generics):
                continue
            sig = "%s:%s" %(method.getName(), signature(method, True))
            # Apparently, overridden clone() methods are still returned via
            # getDeclaredMethods(), so keep the one with the more precise
            # return type, equal to cls.
            if sig in methods and returnType != cls:
                continue
            if generics:
                params = method.getGenericParameterTypes()
            else:
                params = method.getParameterTypes()
            for param in params:
                if not known(param, typeset, declares, packages, excludes,
                             generics):
                    break
            else:
                methods[sig] = method
        elif Modifier.isProtected(modifiers):
            protectedMethods.append(method)

    def _compare(m0, m1):
        value = cmp(m0.getName(), m1.getName())
        if value == 0:
            value = len(m0.getParameterTypes()) - len(m1.getParameterTypes())
        return value

    methods = methods.values()
    sort(methods, fn=_compare)
    methodNames = set([cppname(method.getName()) for method in methods])

    for constructor in constructors:
        if generics:
            exceptions = constructor.getGenericExceptionTypes()
        else:
            exceptions = constructor.getExceptionTypes()
        for exception in exceptions:
            known(exception, typeset, declares, packages, excludes, generics)
    for method in methods:
        if generics:
            exceptions = method.getGenericExceptionTypes()
        else:
            exceptions = method.getExceptionTypes()
        for exception in exceptions:
            known(exception, typeset, declares, packages, excludes, generics)

    fields = []
    instanceFields = []
    for field in cls.getDeclaredFields():
        modifiers = field.getModifiers()
        if (Modifier.isPublic(modifiers) or
            field.getName() in listedMethodOrFieldNames):
            if generics:
                fieldType = field.getGenericType()
            else:
                fieldType = field.getType()
            if not known(fieldType, typeset, declares, packages, excludes,
                         generics):
                continue
            if Modifier.isStatic(modifiers):
                fields.append(field)
            else:
                instanceFields.append(field)
    sort(fields, key=lambda x: x.getName())
    sort(instanceFields, key=lambda x: x.getName())

    line(out)
    superNames = superClsName.split('.')
    line(out, 0, '#include "%s.h"', '/'.join(superNames))

    line(out, 0)
    namespaces = {}
    for declare in declares:
        namespace = namespaces
        if declare not in (cls, superCls):
            declareNames = declare.getName().split('.')
            for declareName in declareNames[:-1]:
                namespace = namespace.setdefault(declareName, {})
            namespace[declareNames[-1]] = True
    forward(out, namespaces, 0)
    line(out, 0, 'template<class T> class JArray;')

    indent = 0;
    line(out)
    for name in names[:-1]:
        line(out, indent, 'namespace %s {', cppname(name))
        indent += 1

    line(out)
    if superClsName == 'JObject':
        line(out, indent, 'class %s%s : public JObject {',
             _dll_export, cppname(names[-1]))
    else:
        line(out, indent, 'class %s%s : public %s {',
             _dll_export, cppname(names[-1]), absname(cppnames(superNames)))
        
    line(out, indent, 'public:')
    indent += 1

    if methods or protectedMethods or constructors:
        line(out, indent, 'enum {')
        for constructor in constructors:
            line(out, indent + 1, 'mid_init$_%s,',
                 env.strhash(signature(constructor)))
        for method in methods:
            line(out, indent + 1, 'mid_%s_%s,', method.getName(),
                 env.strhash(signature(method)))
        for method in protectedMethods:
            line(out, indent + 1, 'mid_%s_%s,', method.getName(),
                 env.strhash(signature(method)))
        line(out, indent + 1, 'max_mid')
        line(out, indent, '};')

    if instanceFields:
        line(out)
        line(out, indent, 'enum {')
        for field in instanceFields:
            line(out, indent + 1, 'fid_%s,', field.getName())
        line(out, indent + 1, 'max_fid')
        line(out, indent, '};')

    line(out)
    line(out, indent, 'static ::java::lang::Class *class$;');
    line(out, indent, 'static jmethodID *mids$;');
    if instanceFields:
        line(out, indent, 'static jfieldID *fids$;');
    line(out, indent, 'static bool live$;');
    line(out, indent, 'static jclass initializeClass(bool);');
    line(out)

    line(out, indent, 'explicit %s(jobject obj) : %s(obj) {',
         cppname(names[-1]), absname(cppnames(superNames)))
    line(out, indent + 1, 'if (obj != NULL)');
    line(out, indent + 2, 'env->getClass(initializeClass);')
    line(out, indent, '}')
    line(out, indent, '%s(const %s& obj) : %s(obj) {}',
         cppname(names[-1]), cppname(names[-1]),
         absname(cppnames(superNames)))

    if fields:
        line(out)
        for field in fields:
            fieldType = field.getType()
            fieldName = cppname(field.getName())
            if fieldName in methodNames:
                print >>sys.stderr, "  Warning: renaming static variable '%s' on class %s to '%s%s' since it is shadowed by a method of same name." %(fieldName, '.'.join(names), fieldName, RENAME_FIELD_SUFFIX)
                fieldName += RENAME_FIELD_SUFFIX
            if fieldType.isPrimitive():
                line(out, indent, 'static %s %s;',
                     typename(fieldType, cls, False), fieldName)
            else:
                line(out, indent, 'static %s *%s;',
                     typename(fieldType, cls, False), fieldName)

    if instanceFields:
        line(out)
        for field in instanceFields:
            fieldType = field.getType()
            fieldName = field.getName()
            modifiers = field.getModifiers()
            line(out, indent, '%s _get_%s() const;',
                 typename(fieldType, cls, False), fieldName)
            if not Modifier.isFinal(modifiers):
                line(out, indent, 'void _set_%s(%s) const;',
                     fieldName, typename(fieldType, cls, True))

    if constructors:
        line(out)
        for constructor in constructors:
            params = [typename(param, cls, True)
                      for param in constructor.getParameterTypes()]
            line(out, indent, '%s(%s);', cppname(names[-1]), ', '.join(params))

    if methods:
        line(out)
        for method in methods:
            modifiers = method.getModifiers()
            if Modifier.isStatic(modifiers):
                prefix = 'static '
                const = ''
            else:
                prefix = ''
                const = ' const'
            params = [typename(param, cls, True)
                      for param in method.getParameterTypes()]
            methodName = cppname(method.getName())
            line(out, indent, '%s%s %s(%s)%s;',
                 prefix, typename(method.getReturnType(), cls, False),
                 methodName, ', '.join(params), const)

    indent -= 1
    line(out, indent, '};')

    while indent:
        indent -= 1
        line(out, indent, '}')

    return (superCls, constructors, methods, protectedMethods,
            methodNames, fields, instanceFields, declares)


def code(env, out, cls, superCls, constructors, methods, protectedMethods,
         methodNames, fields, instanceFields, declares, typeset):

    className = cls.getName()
    names = className.split('.')

    if superCls:
        superClsName = superCls.getName()
    else:
        superClsName = 'JObject'
    superNames = superClsName.split('.')

    line(out, 0, '#include <jni.h>')
    line(out, 0, '#include "JCCEnv.h"')
    line(out, 0, '#include "%s.h"', className.replace('.', '/'))
    for declare in declares:
        if declare not in (cls, superCls):
            line(out, 0, '#include "%s.h"', declare.getName().replace('.', '/'))
    line(out, 0, '#include "JArray.h"')

    indent = 0
    line(out)
    for name in names[:-1]:
        line(out, indent, 'namespace %s {', cppname(name))
        indent += 1

    line(out)
    line(out, indent, '::java::lang::Class *%s::class$ = NULL;',
         cppname(names[-1]))
    line(out, indent, 'jmethodID *%s::mids$ = NULL;', cppname(names[-1]))
    if instanceFields:
        line(out, indent, 'jfieldID *%s::fids$ = NULL;', cppname(names[-1]))
    line(out, indent, 'bool %s::live$ = false;', cppname(names[-1]))

    for field in fields:
        fieldType = field.getType()
        fieldName = cppname(field.getName())
        if fieldName in methodNames:
            fieldName += RENAME_FIELD_SUFFIX
        typeName = typename(fieldType, cls, False)
        if fieldType.isPrimitive():
            line(out, indent, '%s %s::%s = (%s) 0;',
                 typeName, cppname(names[-1]), fieldName, typeName)
        else:
            line(out, indent, '%s *%s::%s = NULL;',
                 typeName, cppname(names[-1]), fieldName)

    line(out)
    line(out, indent, 'jclass %s::initializeClass(bool getOnly)',
         cppname(names[-1]))
    line(out, indent, '{')
    line(out, indent + 1, 'if (getOnly)')
    line(out, indent + 2, 'return (jclass) (live$ ? class$->this$ : NULL);')
    line(out, indent + 1, 'if (class$ == NULL)')
    line(out, indent + 1, '{')
    line(out, indent + 2, 'jclass cls = (jclass) env->findClass("%s");',
         className.replace('.', '/'))

    if methods or protectedMethods or constructors:
        line(out)
        line(out, indent + 2, 'mids$ = new jmethodID[max_mid];')
        for constructor in constructors:
            sig = signature(constructor)
            line(out, indent + 2,
                 'mids$[mid_init$_%s] = env->getMethodID(cls, "<init>", "%s");',
                 env.strhash(sig), sig)
        isExtension = False
        for method in methods:
            methodName = method.getName()
            if methodName == 'pythonExtension':
                isExtension = True
            sig = signature(method)
            line(out, indent + 2,
                 'mids$[mid_%s_%s] = env->get%sMethodID(cls, "%s", "%s");',
                 methodName, env.strhash(sig),
                 Modifier.isStatic(method.getModifiers()) and 'Static' or '',
                 methodName, sig)
        for method in protectedMethods:
            methodName = method.getName()
            sig = signature(method)
            line(out, indent + 2,
                 'mids$[mid_%s_%s] = env->get%sMethodID(cls, "%s", "%s");',
                 methodName, env.strhash(sig),
                 Modifier.isStatic(method.getModifiers()) and 'Static' or '',
                 methodName, sig)

    if instanceFields:
        line(out)
        line(out, indent + 2, 'fids$ = new jfieldID[max_fid];')
        for field in instanceFields:
            fieldName = field.getName()
            line(out, indent + 2,
                 'fids$[fid_%s] = env->getFieldID(cls, "%s", "%s");',
                 fieldName, fieldName, signature(field))

    line(out)
    line(out, indent + 2, 'class$ = (::java::lang::Class *) new JObject(cls);')

    if fields:
        line(out, indent + 2, 'cls = (jclass) class$->this$;')
        line(out)
        for field in fields:
            fieldType = field.getType()
            fieldName = field.getName()
            cppFieldName = cppname(fieldName)
            if cppFieldName in methodNames:
                cppFieldName += RENAME_FIELD_SUFFIX
            if fieldType.isPrimitive():
                line(out, indent + 2,
                     '%s = env->getStatic%sField(cls, "%s");',
                     cppFieldName, fieldType.getName().capitalize(),
                     fieldName)
            else:
                line(out, indent + 2,
                     '%s = new %s(env->getStaticObjectField(cls, "%s", "%s"));',
                     cppFieldName, typename(fieldType, cls, False),
                     fieldName, signature(field))

    line(out, indent + 2, "live$ = true;")
    line(out, indent + 1, '}')
    line(out, indent + 1, 'return (jclass) class$->this$;')
    line(out, indent, '}')

    for constructor in constructors:
        line(out)
        sig = signature(constructor)
        decls, args = argnames(constructor.getParameterTypes(), cls)

        line(out, indent, "%s::%s(%s) : %s(env->newObject(initializeClass, &mids$, mid_init$_%s%s)) {}",
             cppname(names[-1]), cppname(names[-1]), decls,
             absname(cppnames(superNames)),
             env.strhash(sig), args)

    for method in methods:
        modifiers = method.getModifiers()
        returnType = method.getReturnType()
        params = method.getParameterTypes()
        methodName = method.getName()
        superMethod = None
        isStatic = Modifier.isStatic(modifiers)

        if (isExtension and not isStatic and superCls and
            Modifier.isNative(modifiers)):
            superMethod = find_method(superCls, methodName, params)
            if superMethod is None:
                continue

        if isStatic:
            qualifier = 'Static'
            this = 'cls'
            midns = ''
            const = ''
            sig = signature(method)
        else:
            isStatic = False
            if superMethod is not None:
                qualifier = 'Nonvirtual'
                this = 'this$, (jclass) %s::class$->this$' %(absname(cppnames(superNames)))
                declaringClass = superMethod.getDeclaringClass()
                midns = '%s::' %(typename(declaringClass, cls, False))
                sig = signature(superMethod)
            else:
                qualifier = ''
                this = 'this$'
                midns = ''
                sig = signature(method)
            const = ' const'

        decls, args = argnames(params, cls)

        line(out)
        line(out, indent, '%s %s::%s(%s)%s',
             typename(returnType, cls, False), cppname(names[-1]),
             cppname(methodName), decls, const)
        line(out, indent, '{')
        if isStatic:
            line(out, indent + 1,
                 'jclass cls = env->getClass(initializeClass);');
        if returnType.isPrimitive():
            line(out, indent + 1,
                 '%senv->call%s%sMethod(%s, %smids$[%smid_%s_%s]%s);',
                 not returnType.getName() == 'void' and 'return ' or '',
                 qualifier, returnType.getName().capitalize(), this,
                 midns, midns, methodName, env.strhash(sig), args)
        else:
            line(out, indent + 1,
                 'return %s(env->call%sObjectMethod(%s, %smids$[%smid_%s_%s]%s));',
                 typename(returnType, cls, False), qualifier, this,
                 midns, midns, methodName, env.strhash(sig), args)
        line(out, indent, '}')

    if instanceFields:
        for field in instanceFields:
            fieldType = field.getType()
            fieldName = field.getName()
            line(out)
            line(out, indent, '%s %s::_get_%s() const',
                 typename(fieldType, cls, False), cppname(names[-1]), fieldName)
            line(out, indent, '{')
            if fieldType.isPrimitive():
                line(out, indent + 1,
                     'return env->get%sField(this$, fids$[fid_%s]);',
                     fieldType.getName().capitalize(), fieldName)
            else:
                line(out, indent + 1,
                     'return %s(env->getObjectField(this$, fids$[fid_%s]));',
                     typename(fieldType, cls, False), fieldName)
            line(out, indent, '}')

            if not Modifier.isFinal(field.getModifiers()):
                line(out)
                line(out, indent, 'void %s::_set_%s(%s a0) const',
                     cppname(names[-1]), fieldName,
                     typename(fieldType, cls, True))
                line(out, indent, '{')
                if fieldType.isPrimitive():
                    line(out, indent + 1,
                         'env->set%sField(this$, fids$[fid_%s], a0);',
                         fieldType.getName().capitalize(), fieldName)
                else:
                    line(out, indent + 1,
                         'env->setObjectField(this$, fids$[fid_%s], a0.this$);',
                         fieldName)
                line(out, indent, '}')

    while indent:
        indent -= 1
        line(out, indent, '}')

    return names, superNames


if __name__ == '__main__':
    jcc(sys.argv)
