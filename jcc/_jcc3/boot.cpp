/*
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 */

#include <jni.h>
#include <Python.h>
#include "java/lang/Class.h"
#include "java/lang/RuntimeException.h"
#include "macros.h"

extern PyTypeObject *PY_TYPE(JObject), *PY_TYPE(ConstVariableDescriptor);

PyObject *initJCC(PyObject *module);
PyObject *initVM(PyObject *self, PyObject *args, PyObject *kwds);

namespace java {
    namespace lang {
        void __install__(PyObject *m);
    }
    namespace io {
        void __install__(PyObject *m);
    }
}

PyObject *__initialize__(PyObject *module, PyObject *args, PyObject *kwds)
{
    PyObject *env = initVM(module, args, kwds);

    if (env == NULL)
        return NULL;

    java::lang::Class::initializeClass(false);
    java::lang::RuntimeException::initializeClass(false);

    return env;
}

#include "jccfuncs.h"

extern "C" {

static struct PyModuleDef _jccmodule = {
        PyModuleDef_HEAD_INIT,   /* m_base     */
        "_jcc3",                 /* m_name     */
        "_jcc3 module",          /* m_doc      */
        0,                       /* m_size     */
        jcc_funcs,               /* m_methods  */
        0,                       /* m_reload   */
        0,                       /* m_traverse */
        0,                       /* m_clear    */
        0,                       /* m_free     */
    };

    PyObject *PyInit__jcc3(void)
    {
        PyObject *m = PyModule_Create(&_jccmodule);

        if (!m)
            return NULL;

        initJCC(m);

        INSTALL_STATIC_TYPE(JObject, m);
        PY_TYPE_DEF(JObject).type = PY_TYPE(JObject);

        INSTALL_STATIC_TYPE(ConstVariableDescriptor, m);
        java::lang::__install__(m);
        java::io::__install__(m);

        return m;
    }
}
