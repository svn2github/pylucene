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

#ifndef _macros_H
#define _macros_H

#define OBJ_CALL(action)                                                \
    {                                                                   \
        try {                                                           \
            PythonThreadState state(1);                                 \
            action;                                                     \
        } catch (int e) {                                               \
            switch (e) {                                                \
              case _EXC_PYTHON:                                         \
                return NULL;                                            \
              case _EXC_JAVA:                                           \
                return PyErr_SetJavaError();                            \
              default:                                                  \
                throw;                                                  \
            }                                                           \
        }                                                               \
    }

#define INT_CALL(action)                                                \
    {                                                                   \
        try {                                                           \
            PythonThreadState state(1);                                 \
            action;                                                     \
        } catch (int e) {                                               \
            switch (e) {                                                \
              case _EXC_PYTHON:                                         \
                return -1;                                              \
              case _EXC_JAVA:                                           \
                PyErr_SetJavaError();                                   \
                return -1;                                              \
              default:                                                  \
                throw;                                                  \
            }                                                           \
        }                                                               \
    }


#define DECLARE_METHOD(type, name, flags)               \
    { #name, (PyCFunction) type##_##name, flags, "" }

#define DECLARE_GET_FIELD(type, name)           \
    { #name, (getter) type##_get__##name, NULL, "", NULL }

#define DECLARE_SET_FIELD(type, name)           \
    { #name, NULL, (setter) type##_set__##name, "", NULL }

#define DECLARE_GETSET_FIELD(type, name)        \
    { #name, (getter) type##_get__##name, (setter) type##_set__##name, "", NULL }

struct PyType_Def {
    PyType_Spec spec;
    PyTypeObject *type;
    PyType_Def **bases;   // NULL terminated array
};

#define PY_TYPE(name) name##$$Type
#define PY_TYPE_DEF(name) name##$$TypeDef
#define PY_TYPE_BASES(name) name##$$TypeBases
#define PY_TYPE_SLOTS(name) name##$$TypeSlots

#define DEFINE_TYPE(name, t_name, javaClass)                                \
PyType_Def PY_TYPE_DEF(name) = {                                            \
  {                                                                         \
    #name,                                                                  \
    sizeof(t_name),                                                         \
    0,                                                                      \
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                               \
    PY_TYPE_SLOTS(name)                                                     \
  },                                                                        \
  NULL,                                                                     \
  PY_TYPE_BASES(name),                                                      \
};                                                                          \
PyTypeObject *PY_TYPE(name) = NULL;                                         \
PyObject *t_name::wrap_Object(const javaClass& object)                  \
{                                                                       \
    if (!!object)                                                       \
    {                                                                   \
        t_name *self = (t_name *)                                       \
            PyType_GenericAlloc(PY_TYPE(name), 0);                      \
        if (self)                                                       \
            self->object = object;                                      \
        return (PyObject *) self;                                       \
    }                                                                   \
    Py_RETURN_NONE;                                                     \
}                                                                       \
PyObject *t_name::wrap_jobject(const jobject& object)                   \
{                                                                       \
    if (!!object)                                                       \
    {                                                                   \
        if (!env->isInstanceOf(object, javaClass::initializeClass))     \
        {                                                               \
            PyErr_SetObject(PyExc_TypeError,                            \
                            (PyObject *) PY_TYPE(name));                \
            return NULL;                                                \
        }                                                               \
        t_name *self = (t_name *)                                       \
            PyType_GenericAlloc(PY_TYPE(name), 0);                      \
        if (self)                                                       \
            self->object = javaClass(object);                           \
        return (PyObject *) self;                                       \
    }                                                                   \
    Py_RETURN_NONE;                                                     \
}                                                                       \

#define DECLARE_TYPE(name)                                              \
    extern PyType_Def PY_TYPE_DEF(name);                                \
    extern PyTypeObject *PY_TYPE(name)

#define INSTALL_TYPE(name, module)                                      \
    installType(&PY_TYPE(name), &PY_TYPE_DEF(name), module, #name, 0)

#define INSTALL_STATIC_TYPE(name, module)                               \
    if (PyType_Ready(PY_TYPE(name)) == 0)                               \
    {                                                                   \
        Py_INCREF(PY_TYPE(name));                                       \
        PyModule_AddObject(module, #name, (PyObject *) PY_TYPE(name));  \
    }


#define Py_RETURN_BOOL(b)                       \
    {                                           \
        if (b)                                  \
            Py_RETURN_TRUE;                     \
        else                                    \
            Py_RETURN_FALSE;                    \
    }

#define Py_RETURN_SELF                                      \
    {                                                       \
        Py_INCREF(self);                                    \
        return (PyObject *) self;                           \
    }

#endif /* _macros_H */
