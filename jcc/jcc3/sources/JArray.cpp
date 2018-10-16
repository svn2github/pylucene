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

#ifdef PYTHON

#include <jni.h>
#include <Python.h>
#include "structmember.h"

#include "JArray.h"
#include "functions.h"
#include "java/lang/Class.h"

using namespace java::lang;


template<typename T> class _t_JArray : public t_JArray<T> {
public:
    static PyObject *format;
};

template<typename U>
static PyObject *get(U *self, Py_ssize_t n)
{
    return self->array.get(n);
}

template<typename U>
static PyObject *toSequence(U *self)
{
    return self->array.toSequence();
}

template<typename U>
static PyObject *toSequence(U *self, Py_ssize_t lo, Py_ssize_t hi)
{
    return self->array.toSequence(lo, hi);
}

template<typename U> class _t_iterator {
public:
    PyObject_HEAD
    U *obj;
    Py_ssize_t position;

    static void dealloc(_t_iterator *self)
    {
        Py_XDECREF(self->obj);
        self->ob_base.ob_type->tp_free((PyObject *) self);
    }

    static PyObject *iternext(_t_iterator *self)
    {
        if (self->position < (Py_ssize_t) self->obj->array.length)
            return get<U>(self->obj, self->position++);

        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }

    static PyTypeObject *JArrayIterator;
};

template<typename T, typename U>
static int init(U *self, PyObject *args, PyObject *kwds)
{
    PyObject *obj;

    if (!PyArg_ParseTuple(args, "O", &obj))
        return -1;

    if (PySequence_Check(obj))
    {
        self->array = JArray<T>(obj);
        if (PyErr_Occurred())
            return -1;
    }
    else if (PyGen_Check(obj))
    {
        PyObject *tuple =
            PyObject_CallFunctionObjArgs((PyObject *) &PyTuple_Type, obj, NULL);

        if (!tuple)
            return -1;

        self->array = JArray<T>(tuple);
        Py_DECREF(tuple);
        if (PyErr_Occurred())
            return -1;
    }
    else if (PyLong_Check(obj))
    {
        int n = PyLong_AsLong(obj);

        if (n < 0)
        {
            PyErr_SetObject(PyExc_ValueError, obj);
            return -1;
        }

        self->array = JArray<T>(n);
    }
    else
    {
        PyErr_SetObject(PyExc_TypeError, obj);
        return -1;
    }

    return 0;
}

template<typename T, typename U>
static void dealloc(U *self)
{
    self->array = JArray<T>((jobject) NULL);
    self->ob_base.ob_type->tp_free((PyObject *) self);
}

template<typename U>
static PyObject *_format(U *self, PyObject *(*fn)(PyObject *))
{
    if (self->array.this$)
    {
        PyObject *list = toSequence<U>(self);

        if (list)
        {
            PyObject *result = (*fn)(list);

            Py_DECREF(list);
            if (result)
            {
                PyObject *args = PyTuple_New(1);

                PyTuple_SET_ITEM(args, 0, result);
                result = PyUnicode_Format(U::format, args);
                Py_DECREF(args);

                return result;
            }
        }

        return NULL;
    }

    return PyUnicode_FromString("<null>");
}

template<typename U>
static PyObject *repr(U *self)
{
    return _format(self, (PyObject *(*)(PyObject *)) PyObject_Repr);
}

template<typename U>
static PyObject *str(U *self)
{
    return _format(self, (PyObject *(*)(PyObject *)) PyObject_Str);
}

template<typename U>
static int _compare(U *self, PyObject *value, int i0, int i1, int op, int *cmp)
{
    PyObject *v0 = get<U>(self, i0);
    PyObject *v1 = PySequence_Fast_GET_ITEM(value, i1);  /* borrowed */

    if (!v0)
        return -1;

    if (!v1)
    {
        Py_DECREF(v0);
        return -1;
    }

    *cmp = PyObject_RichCompareBool(v0, v1, op);
    Py_DECREF(v0);

    if (*cmp < 0)
        return -1;

    return 0;
}

template<typename U>
static PyObject *richcompare(U *self, PyObject *value, int op)
{
    PyObject *result = NULL;
    int s0, s1;

    if (!PySequence_Check(value))
    {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    value = PySequence_Fast(value, "not a sequence");
    if (!value)
        return NULL;

    s0 = PySequence_Fast_GET_SIZE(value);
    s1 = self->array.length;

    if (s1 < 0)
    {
        Py_DECREF(value);
        return NULL;
    }

    if (s0 != s1)
    {
        switch (op) {
          case Py_EQ: result = Py_False; break;
          case Py_NE: result = Py_True; break;
        }
    }

    if (!result)
    {
        int i0, i1, cmp = 1;

        for (i0 = 0, i1 = 0; i0 < s0 && i1 < s1 && cmp; i0++, i1++) {
            if (_compare(self, value, i0, i1, Py_EQ, &cmp) < 0)
            {
                Py_DECREF(value);
                return NULL;
            }
        }

        if (cmp)
        {
            switch (op) {
              case Py_LT: cmp = s0 < s1; break;
              case Py_LE: cmp = s0 <= s1; break;
              case Py_EQ: cmp = s0 == s1; break;
              case Py_NE: cmp = s0 != s1; break;
              case Py_GT: cmp = s0 > s1; break;
              case Py_GE: cmp = s0 >= s1; break;
              default: cmp = 0;
            }

            result = cmp ? Py_True : Py_False;
        }
        else if (op == Py_EQ)
            result = Py_False;
        else if (op == Py_NE)
            result = Py_True;
        else if (_compare(self, value, i0, i1, op, &cmp) < 0)
        {
            Py_DECREF(value);
            return NULL;
        }
        else
            result = cmp ? Py_True : Py_False;
    }
    Py_DECREF(value);

    Py_INCREF(result);
    return result;
}

template<typename U>
static PyObject *iter(U *self)
{
    _t_iterator<U> *it =
        PyObject_New(_t_iterator<U>, _t_iterator<U>::JArrayIterator);

    if (it)
    {
        it->position = 0;
        it->obj = self; Py_INCREF((PyObject *) self);
    }

    return (PyObject *) it;
}

template<typename U>
static Py_ssize_t seq_length(U *self)
{
    if (self->array.this$)
        return self->array.length;

    return 0;
}

template<typename U>
static PyObject *seq_get(U *self, Py_ssize_t n)
{
    return get<U>(self, n);
}

template<typename U>
static int seq_contains(U *self, PyObject *value)
{
    return 0;
}

template<typename U>
static PyObject *seq_concat(U *self, PyObject *arg)
{
    PyObject *list = toSequence<U>(self);

    if (list != NULL &&
        PyList_Type.tp_as_sequence->sq_inplace_concat(list, arg) == NULL)
    {
        Py_DECREF(list);
        return NULL;
    }

    return list;
}

template<typename U>
static PyObject *seq_repeat(U *self, Py_ssize_t n)
{
    PyObject *list = toSequence<U>(self);

    if (list != NULL &&
        PyList_Type.tp_as_sequence->sq_inplace_repeat(list, n) == NULL)
    {
        Py_DECREF(list);
        return NULL;
    }

    return list;
}

template<typename U>
static int seq_set(U *self, Py_ssize_t n, PyObject *value)
{
    return self->array.set(n, value);
}

template<typename U>
static PyObject *seq_getslice(U *self, Py_ssize_t lo, Py_ssize_t hi)
{
    return toSequence<U>(self, lo, hi);
}

template<typename U>
static int seq_setslice(U *self, Py_ssize_t lo, Py_ssize_t hi, PyObject *values)
{
    Py_ssize_t length = self->array.length;

    if (values == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "array size cannot change");
        return -1;
    }

    if (lo < 0) lo = length + lo;
    if (lo < 0) lo = 0;
    else if (lo > length) lo = length;
    if (hi < 0) hi = length + hi;
    if (hi < 0) hi = 0;
    else if (hi > length) hi = length;
    if (lo > hi) lo = hi;

    PyObject *sequence = PySequence_Fast(values, "not a sequence");
    if (!sequence)
        return -1;

    Py_ssize_t size = PySequence_Fast_GET_SIZE(sequence);
    if (size < 0)
        goto error;

    if (size != hi - lo)
    {
        PyErr_SetString(PyExc_ValueError, "array size cannot change");
        goto error;
    }

    for (Py_ssize_t i = lo; i < hi; i++) {
        PyObject *value = PySequence_Fast_GET_ITEM(sequence, i - lo);

        if (value == NULL)
            goto error;

        if (self->array.set(i, value) < 0)
            goto error;
    }

    Py_DECREF(sequence);
    return 0;

  error:
    Py_DECREF(sequence);
    return -1;
}


template<typename U>
static PyObject *map_subscript(U *self, PyObject *key)
{
    if (PySlice_Check(key))
    {
        Py_ssize_t from, to, step, slicelength;

        if (PySlice_GetIndicesEx(key, seq_length(self), &from, &to, &step,
                                 &slicelength) < 0)
            return NULL;

        if (step != 1)
        {
            PyErr_SetString(PyExc_ValueError, "slice step must be 1");
            return NULL;
        }

        return seq_getslice<U>(self, from, to);
    }

    if (PyIndex_Check(key))
    {
        Py_ssize_t at = PyNumber_AsSsize_t(key, PyExc_IndexError);

        if (at == -1 && PyErr_Occurred())
            return NULL;

        return seq_get<U>(self, at);
    }

    PyErr_SetObject(PyExc_TypeError, key);
    return NULL;
}

template<typename U>
static int map_ass_subscript(U *self, PyObject *key, PyObject *value)
{
    if (PySlice_Check(key))
    {
        Py_ssize_t from, to, step, slicelength;

        if (PySlice_GetIndicesEx(key, seq_length(self), &from, &to, &step,
                                 &slicelength) < 0)
            return -1;

        if (step != 1)
        {
            PyErr_SetString(PyExc_ValueError, "slice step must be 1");
            return -1;
        }

        return seq_setslice<U>(self, from, to, value);
    }

    if (PyIndex_Check(key))
    {
        Py_ssize_t at = PyNumber_AsSsize_t(key, PyExc_IndexError);

        if (at == -1 && PyErr_Occurred())
            return -1;

        return seq_set<U>(self, at, value);
    }

    PyErr_SetObject(PyExc_TypeError, key);
    return -1;
}


static PyObject *t_JArray_jbyte__get_string_(t_JArray<jbyte> *self, void *data)
{
    return self->array.to_string_();
}

static PyObject *t_JArray_jbyte__get_bytes_(t_JArray<jbyte> *self, void *data)
{
    return self->array.to_bytes_();
}

static PyGetSetDef t_JArray_jbyte__fields[] = {
  { "string_", (getter) t_JArray_jbyte__get_string_, NULL, "", NULL },
  { "bytes_", (getter) t_JArray_jbyte__get_bytes_, NULL, "", NULL },
  { NULL, NULL, NULL, NULL, NULL }
};


template<typename T>
static jclass initializeClass(bool getOnly)
{
    return env->get_vm_env()->GetObjectClass(JArray<T>((Py_ssize_t) 0).this$);
}

template<typename T>
static PyObject *cast_(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *arg, *clsObj;

    if (!PyArg_ParseTuple(args, "O", &arg))
        return NULL;

    if (!PyObject_TypeCheck(arg, PY_TYPE(Object)))
    {
        PyErr_SetObject(PyExc_TypeError, arg);
        return NULL;
    }

    Class argCls = ((t_Object *) arg)->object.getClass();

    if (!argCls.isArray())
    {
        PyErr_SetObject(PyExc_TypeError, arg);
        return NULL;
    }

    clsObj = PyObject_GetAttrString((PyObject *) type, "class_");
    if (!clsObj)
        return NULL;

    Class arrayCls = ((t_Class *) clsObj)->object;

    if (!arrayCls.isAssignableFrom(argCls))
    {
        PyErr_SetObject(PyExc_TypeError, arg);
        return NULL;
    }

    return JArray<T>(((t_JObject *) arg)->object.this$).wrap();
}

template<typename T>
static PyObject *wrapfn_(const jobject &object) {
    return JArray<T>(object).wrap();
}

template<typename T>
static PyObject *instance_(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *arg, *clsObj;

    if (!PyArg_ParseTuple(args, "O", &arg))
        return NULL;

    if (!PyObject_TypeCheck(arg, PY_TYPE(Object)))
        Py_RETURN_FALSE;

    Class argCls = ((t_Object *) arg)->object.getClass();

    if (!argCls.isArray())
        Py_RETURN_FALSE;

    clsObj = PyObject_GetAttrString((PyObject *) type, "class_");
    if (!clsObj)
        return NULL;

    Class arrayCls = ((t_Class *) clsObj)->object;

    if (!arrayCls.isAssignableFrom(argCls))
        Py_RETURN_FALSE;

    Py_RETURN_TRUE;
}

template<typename T>
static PyObject *assignable_(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    return instance_<T>(type, args, kwds);
}

template< typename T, typename U = _t_JArray<T> > class jarray_type {
public:
    PyTypeObject *type_object;

    class iterator_type {
    public:
        PyTypeObject *type_object;

        void install(char *name, PyObject *module)
        {
            PyType_Slot slots[] = {
                { Py_tp_dealloc, (void *) _t_iterator<U>::dealloc },
                { Py_tp_doc, (void *) "JArrayIterator<T> wrapper type" },
                { Py_tp_iter, (void *) PyObject_SelfIter },
                { Py_tp_iternext, (void *) _t_iterator<U>::iternext },
                { 0, NULL }
            };

            PyType_Spec spec = {
                name, 
                sizeof(_t_iterator<U>),
                0,
                Py_TPFLAGS_DEFAULT,
                slots
            };

            type_object = (PyTypeObject *) PyType_FromSpec(&spec);

            if (type_object != NULL)
                PyModule_AddObject(module, name, (PyObject *) type_object);

            _t_iterator<U>::JArrayIterator = type_object;
        }
    };

    iterator_type iterator_type_object;

    void install(char *name, char *type_name, char *iterator_name,
                 PyObject *module)
    {
        static PyMethodDef methods[] = {
            { "cast_",
              (PyCFunction) cast_<T>, METH_VARARGS | METH_CLASS, "" },
            { "instance_",
              (PyCFunction) instance_<T>, METH_VARARGS | METH_CLASS, "" },
            { "assignable_",
              (PyCFunction) assignable_<T>, METH_VARARGS | METH_CLASS, "" },
            { NULL, NULL, 0, NULL }
        };

        PyType_Slot slots[] = {
            { Py_tp_dealloc, (void *) dealloc<T,U> },
            { Py_tp_repr, (void *) repr<U> },
            { Py_sq_length, (void *) seq_length<U> },
            { Py_sq_concat, (void *) seq_concat<U> },
            { Py_sq_repeat, (void *) seq_repeat<U> },
            { Py_sq_item, (void *) seq_get<U> },
            { Py_sq_ass_item, (void *) seq_set<U> },
            { Py_sq_contains, (void *) seq_contains<U> },
            { Py_mp_length, (void *) seq_length<U> },
            { Py_mp_subscript, (void *) map_subscript<U> },
            { Py_mp_ass_subscript, (void *) map_ass_subscript<U> },
            { Py_tp_str, (void *) str<U> },
            { Py_tp_doc, (void *) "JArray<T> wrapper type" },
            { Py_tp_richcompare, (void *) richcompare<U> },
            { Py_tp_iter, (void *) iter<U> },
            { Py_tp_methods, methods },
            { Py_tp_init, (void *) init<T,U> },
            { Py_tp_new, (void *) _new },
            { 0, NULL },  // to patch in byte[].string_ and bytes_
            { 0, NULL }
        };

        if (!strcmp(type_name, "byte"))
        {
            slots[(sizeof(slots) / sizeof(PyType_Slot)) - 2] = {
                Py_tp_getset, (void *) t_JArray_jbyte__fields
            };
        }

        PyType_Spec spec = {
            name, 
            sizeof(U),
            0,
            Py_TPFLAGS_DEFAULT,
            slots
        };

        PyObject *bases = PyTuple_Pack(1, PY_TYPE(Object));

        type_object = (PyTypeObject *) PyType_FromSpecWithBases(&spec, bases);
        Py_DECREF(bases);

        if (type_object != NULL)
        {
            PyDict_SetItemString(type_object->tp_dict, "class_",
                                 make_descriptor(initializeClass<T>));
            PyDict_SetItemString(type_object->tp_dict, "wrapfn_",
                                 make_descriptor(wrapfn_<T>));

            PyModule_AddObject(module, name, (PyObject *) type_object);
        }

        U::format = PyUnicode_FromFormat("JArray<%s>%%s", type_name);
        iterator_type_object.install(iterator_name, module);
    }

    static PyObject *_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
    {
        U *self = (U *) type->tp_alloc(type, 0);

        if (self)
            self->array = JArray<T>((jobject) NULL);

        return (PyObject *) self;
    }
};

template<typename T> class _t_jobjectarray : public _t_JArray<T> {
public:
    PyObject *(*wrapfn)(const T&);
};

template<> PyObject *get(_t_jobjectarray<jobject> *self, Py_ssize_t n)
{
    return self->array.get(n, self->wrapfn);
}

template<> PyObject *toSequence(_t_jobjectarray<jobject> *self)
{
    return self->array.toSequence(self->wrapfn);
}
template<> PyObject *toSequence(_t_jobjectarray<jobject> *self,
                                Py_ssize_t lo, Py_ssize_t hi)
{
    return self->array.toSequence(lo, hi, self->wrapfn);
}

template<> int init< jobject,_t_jobjectarray<jobject> >(_t_jobjectarray<jobject> *self, PyObject *args, PyObject *kwds)
{
    PyObject *obj, *clsObj = NULL;
    PyObject *(*wrapfn)(const jobject &) = NULL;
    jclass cls;

    if (!PyArg_ParseTuple(args, "O|O", &obj, &clsObj))
        return -1;

    if (clsObj == NULL)
        cls = env->findClass("java/lang/Object");
    else if (PyObject_TypeCheck(clsObj, PY_TYPE(Class)))
        cls = (jclass) ((t_Class *) clsObj)->object.this$;
    else if (PyType_Check(clsObj))
    {
        if (PyType_IsSubtype((PyTypeObject *) clsObj, PY_TYPE(JObject)))
        {
            PyObject *cobj = PyObject_GetAttrString(clsObj, "wrapfn_");

            if (cobj == NULL)
                PyErr_Clear();
            else
            {
                wrapfn = (PyObject *(*)(const jobject &))
                    PyCapsule_GetPointer(cobj, "wrapfn");
                Py_DECREF(cobj);
            }

            clsObj = PyObject_GetAttrString(clsObj, "class_");
            if (clsObj == NULL)
                return -1;

            cls = (jclass) ((t_Class *) clsObj)->object.this$;
            Py_DECREF(clsObj);
        }
        else
        {
            PyErr_SetObject(PyExc_ValueError, clsObj);
            return -1;
        }
    }
    else
    {
        PyErr_SetObject(PyExc_TypeError, clsObj);
        return -1;
    }

    if (PySequence_Check(obj))
    {
        self->array = JArray<jobject>(cls, obj);
        if (PyErr_Occurred())
            return -1;
    }
    else if (PyGen_Check(obj))
    {
        PyObject *tuple =
            PyObject_CallFunctionObjArgs((PyObject *) &PyTuple_Type, obj, NULL);

        if (!tuple)
            return -1;

        self->array = JArray<jobject>(cls, tuple);
        Py_DECREF(tuple);
        if (PyErr_Occurred())
            return -1;
    }
    else if (PyLong_Check(obj))
    {
        int n = PyLong_AsLong(obj);

        if (n < 0)
        {
            PyErr_SetObject(PyExc_ValueError, obj);
            return -1;
        }

        self->array = JArray<jobject>(cls, n);
    }
    else
    {
        PyErr_SetObject(PyExc_TypeError, obj);
        return -1;
    }

    self->wrapfn = wrapfn;

    return 0;
}

template<> jclass initializeClass<jobject>(bool getOnly)
{
    jclass cls = env->findClass("java/lang/Object");
    return env->get_vm_env()->GetObjectClass(JArray<jobject>(cls, (Py_ssize_t) 0).this$);
}

template<> PyObject *cast_<jobject>(PyTypeObject *type,
				    PyObject *args, PyObject *kwds)
{
    PyObject *arg, *clsArg = NULL;
    PyObject *(*wrapfn)(const jobject&) = NULL;
    jclass elementCls;

    if (!PyArg_ParseTuple(args, "O|O", &arg, &clsArg))
        return NULL;

    if (!PyObject_TypeCheck(arg, PY_TYPE(Object)))
    {
        PyErr_SetObject(PyExc_TypeError, arg);
        return NULL;
    }

    Class argCls = ((t_Object *) arg)->object.getClass();

    if (!argCls.isArray())
    {
        PyErr_SetObject(PyExc_TypeError, arg);
        return NULL;
    }

    if (clsArg != NULL)
    {
        if (!PyType_Check(clsArg))
        {
            PyErr_SetObject(PyExc_TypeError, clsArg);
            return NULL;
        }
        else if (!PyType_IsSubtype((PyTypeObject *) clsArg, PY_TYPE(JObject)))
        {
            PyErr_SetObject(PyExc_ValueError, clsArg);
            return NULL;
        }

        PyObject *cobj = PyObject_GetAttrString(clsArg, "wrapfn_");

        if (cobj == NULL)
            PyErr_Clear();
        else
        {
            wrapfn = (PyObject *(*)(const jobject &))
                PyCapsule_GetPointer(cobj, "wrapfn");
            Py_DECREF(cobj);
        }

        clsArg = PyObject_GetAttrString(clsArg, "class_");
        if (clsArg == NULL)
            return NULL;

        elementCls = (jclass) ((t_Class *) clsArg)->object.this$;
        Py_DECREF(clsArg);
    }
    else
        elementCls = env->findClass("java/lang/Object");

    JNIEnv *vm_env = env->get_vm_env();
    jobjectArray array = vm_env->NewObjectArray(0, elementCls, NULL);
    Class arrayCls(vm_env->GetObjectClass((jobject) array));

    if (!arrayCls.isAssignableFrom(argCls))
    {
        PyErr_SetObject(PyExc_TypeError, arg);
        return NULL;
    }

    return JArray<jobject>(((t_JObject *) arg)->object.this$).wrap(wrapfn);
}

template<> PyObject *wrapfn_<jobject>(const jobject &object) {
    PyObject *cobj = PyObject_GetAttrString(
        (PyObject *) PY_TYPE(Object), "wrapfn_");
    PyObject *(*wrapfn)(const jobject&) = NULL;

    if (cobj == NULL)
        PyErr_Clear();
    else
    {
        wrapfn = (PyObject *(*)(const jobject &))
            PyCapsule_GetPointer(cobj, "wrapfn");

        Py_DECREF(cobj);
    }

    return JArray<jobject>(object).wrap(wrapfn);
}

template<> PyObject *instance_<jobject>(PyTypeObject *type,
					PyObject *args, PyObject *kwds)
{
    PyObject *arg, *clsArg = NULL;
    jclass elementCls;

    if (!PyArg_ParseTuple(args, "O|O", &arg, &clsArg))
        return NULL;

    if (!PyObject_TypeCheck(arg, PY_TYPE(Object)))
        Py_RETURN_FALSE;

    Class argCls = ((t_Object *) arg)->object.getClass();

    if (!argCls.isArray())
        Py_RETURN_FALSE;

    if (clsArg != NULL)
    {
        if (!PyType_Check(clsArg))
        {
            PyErr_SetObject(PyExc_TypeError, clsArg);
            return NULL;
        }
        else if (!PyType_IsSubtype((PyTypeObject *) clsArg, PY_TYPE(JObject)))
        {
            PyErr_SetObject(PyExc_ValueError, clsArg);
            return NULL;
        }

        clsArg = PyObject_GetAttrString(clsArg, "class_");
        if (clsArg == NULL)
            return NULL;

        elementCls = (jclass) ((t_Class *) clsArg)->object.this$;
        Py_DECREF(clsArg);
    }
    else
        elementCls = env->findClass("java/lang/Object");

    JNIEnv *vm_env = env->get_vm_env();
    jobjectArray array = vm_env->NewObjectArray(0, elementCls, NULL);
    Class arrayCls(vm_env->GetObjectClass((jobject) array));

    if (!arrayCls.isAssignableFrom(argCls))
        Py_RETURN_FALSE;

    Py_RETURN_TRUE;
}

template<> PyObject *assignable_<jobject>(PyTypeObject *type,
					  PyObject *args, PyObject *kwds)
{
    PyObject *arg, *clsArg = NULL;
    jclass elementCls;

    if (!PyArg_ParseTuple(args, "O|O", &arg, &clsArg))
        return NULL;

    if (!PyObject_TypeCheck(arg, PY_TYPE(Object)))
        Py_RETURN_FALSE;

    Class argCls = ((t_Object *) arg)->object.getClass();

    if (!argCls.isArray())
        Py_RETURN_FALSE;

    if (clsArg != NULL)
    {
        if (!PyType_Check(clsArg))
        {
            PyErr_SetObject(PyExc_TypeError, clsArg);
            return NULL;
        }
        else if (!PyType_IsSubtype((PyTypeObject *) clsArg, PY_TYPE(JObject)))
        {
            PyErr_SetObject(PyExc_ValueError, clsArg);
            return NULL;
        }

        clsArg = PyObject_GetAttrString(clsArg, "class_");
        if (clsArg == NULL)
            return NULL;

        elementCls = (jclass) ((t_Class *) clsArg)->object.this$;
        Py_DECREF(clsArg);
    }
    else
        elementCls = env->findClass("java/lang/Object");

    JNIEnv *vm_env = env->get_vm_env();
    jobjectArray array = vm_env->NewObjectArray(0, elementCls, NULL);
    Class arrayCls(vm_env->GetObjectClass((jobject) array));

    if (!argCls.isAssignableFrom(arrayCls))
        Py_RETURN_FALSE;

    Py_RETURN_TRUE;
}


template<typename T> PyTypeObject *_t_iterator<T>::JArrayIterator;
template<typename T> PyObject *_t_JArray<T>::format;

static jarray_type< jobject, _t_jobjectarray<jobject> > jarray_jobject;

static jarray_type<jstring> jarray_jstring;
static jarray_type<jboolean> jarray_jboolean;
static jarray_type<jbyte> jarray_jbyte;
static jarray_type<jchar> jarray_jchar;
static jarray_type<jdouble> jarray_jdouble;
static jarray_type<jfloat> jarray_jfloat;
static jarray_type<jint> jarray_jint;
static jarray_type<jlong> jarray_jlong;
static jarray_type<jshort> jarray_jshort;


PyObject *JArray<jobject>::wrap(PyObject *(*wrapfn)(const jobject&)) const
{
    if (this$ != NULL)
    {
        _t_jobjectarray<jobject> *obj =
            PyObject_New(_t_jobjectarray<jobject>, jarray_jobject.type_object);

        memset((void *) &(obj->array), 0, sizeof(JArray<jobject>));
        obj->array = *this;
        obj->wrapfn = wrapfn;

        return (PyObject *) obj;
    }

    Py_RETURN_NONE;
}

PyObject *JArray<jstring>::wrap() const
{
    if (this$ != NULL)
    {
        _t_JArray<jstring> *obj =
            PyObject_New(_t_JArray<jstring>, jarray_jstring.type_object);

        memset((void *) &(obj->array), 0, sizeof(JArray<jstring>));
        obj->array = *this;

        return (PyObject *) obj;
    }

    Py_RETURN_NONE;
}

PyObject *JArray<jboolean>::wrap() const
{
    if (this$ != NULL)
    {
        _t_JArray<jboolean> *obj =
            PyObject_New(_t_JArray<jboolean>, jarray_jboolean.type_object);

        memset((void *) &(obj->array), 0, sizeof(JArray<jboolean>));
        obj->array = *this;

        return (PyObject *) obj;
    }

    Py_RETURN_NONE;
}

PyObject *JArray<jbyte>::wrap() const
{
    if (this$ != NULL)
    {
        _t_JArray<jbyte> *obj =
            PyObject_New(_t_JArray<jbyte>, jarray_jbyte.type_object);

        memset((void *) &(obj->array), 0, sizeof(JArray<jbyte>));
        obj->array = *this;

        return (PyObject *) obj;
    }

    Py_RETURN_NONE;
}

PyObject *JArray<jchar>::wrap() const
{
    if (this$ != NULL)
    {
        _t_JArray<jchar> *obj =
            PyObject_New(_t_JArray<jchar>, jarray_jchar.type_object);

        memset((void *) &(obj->array), 0, sizeof(JArray<jchar>));
        obj->array = *this;

        return (PyObject *) obj;
    }

    Py_RETURN_NONE;
}

PyObject *JArray<jdouble>::wrap() const
{
    if (this$ != NULL)
    {
        _t_JArray<jdouble> *obj =
            PyObject_New(_t_JArray<jdouble>, jarray_jdouble.type_object);

        memset((void *) &(obj->array), 0, sizeof(JArray<jdouble>));
        obj->array = *this;

        return (PyObject *) obj;
    }

    Py_RETURN_NONE;
}

PyObject *JArray<jfloat>::wrap() const
{
    if (this$ != NULL)
    {
        _t_JArray<jfloat> *obj =
            PyObject_New(_t_JArray<jfloat>, jarray_jfloat.type_object);

        memset((void *) &(obj->array), 0, sizeof(JArray<jfloat>));
        obj->array = *this;

        return (PyObject *) obj;
    }

    Py_RETURN_NONE;
}

PyObject *JArray<jint>::wrap() const
{
    if (this$ != NULL)
    {
        _t_JArray<jint> *obj =
            PyObject_New(_t_JArray<jint>, jarray_jint.type_object);

        memset((void *) &(obj->array), 0, sizeof(JArray<jint>));
        obj->array = *this;

        return (PyObject *) obj;
    }

    Py_RETURN_NONE;
}

PyObject *JArray<jlong>::wrap() const
{
    if (this$ != NULL)
    {
        _t_JArray<jlong> *obj =
            PyObject_New(_t_JArray<jlong>, jarray_jlong.type_object);

        memset((void *) &(obj->array), 0, sizeof(JArray<jlong>));
        obj->array = *this;

        return (PyObject *) obj;
    }

    Py_RETURN_NONE;
}

PyObject *JArray<jshort>::wrap() const
{
    if (this$ != NULL)
    {
        _t_JArray<jshort> *obj =
            PyObject_New(_t_JArray<jshort>, jarray_jshort.type_object);

        memset((void *) &(obj->array), 0, sizeof(JArray<jshort>));
        obj->array = *this;

        return (PyObject *) obj;
    }

    Py_RETURN_NONE;
}

PyObject *JArray_Type(PyObject *self, PyObject *arg)
{
    PyObject *type_name = NULL, *type;
    char const *name = NULL;

    if (PyType_Check(arg))
    {
        type_name = PyObject_GetAttrString(arg, "__name__");
        if (!type_name)
            return NULL;
    }
    else if (PyUnicode_Check(arg))
    {
        type_name = arg;
        Py_INCREF(type_name);
    }
    else if (PyFloat_Check(arg))
    {
        type_name = NULL;
        name = "double";
    }
    else
    {
        PyObject *arg_type = (PyObject *) arg->ob_type;

        type_name = PyObject_GetAttrString(arg_type, "__name__");
        if (!type_name)
            return NULL;
    }

    if (type_name != NULL)
    {
        name = PyUnicode_AsUTF8(type_name);
        if (!name)
        {
            Py_DECREF(type_name);
            return NULL;
        }
    }

    if (!strcmp(name, "object"))
        type = (PyObject *) jarray_jobject.type_object;
    else if (!strcmp(name, "string"))
        type = (PyObject *) jarray_jstring.type_object;
    else if (!strcmp(name, "bool"))
        type = (PyObject *) jarray_jboolean.type_object;
    else if (!strcmp(name, "byte"))
        type = (PyObject *) jarray_jbyte.type_object;
    else if (!strcmp(name, "char"))
        type = (PyObject *) jarray_jchar.type_object;
    else if (!strcmp(name, "double"))
        type = (PyObject *) jarray_jdouble.type_object;
    else if (!strcmp(name, "float"))
        type = (PyObject *) jarray_jfloat.type_object;
    else if (!strcmp(name, "int"))
        type = (PyObject *) jarray_jint.type_object;
    else if (!strcmp(name, "long"))
        type = (PyObject *) jarray_jlong.type_object;
    else if (!strcmp(name, "short"))
        type = (PyObject *) jarray_jshort.type_object;
    else
    {
        PyErr_SetObject(PyExc_ValueError, arg);
        Py_XDECREF(type_name);

        return NULL;
    }

    Py_INCREF(type);
    Py_XDECREF(type_name);

    return type;
}

PyTypeObject *PY_TYPE(JArrayObject);
PyTypeObject *PY_TYPE(JArrayString);
PyTypeObject *PY_TYPE(JArrayBool);
PyTypeObject *PY_TYPE(JArrayByte);
PyTypeObject *PY_TYPE(JArrayChar);
PyTypeObject *PY_TYPE(JArrayDouble);
PyTypeObject *PY_TYPE(JArrayFloat);
PyTypeObject *PY_TYPE(JArrayInt);
PyTypeObject *PY_TYPE(JArrayLong);
PyTypeObject *PY_TYPE(JArrayShort);


void _install_jarray(PyObject *module)
{
    jarray_jobject.install("JArray_object", "object",
                            "__JArray_object_iterator", module);
    PY_TYPE(JArrayObject) = jarray_jobject.type_object;

    jarray_jstring.install("JArray_string", "string",
                            "__JArray_string_iterator", module);
    PY_TYPE(JArrayString) = jarray_jstring.type_object;

    jarray_jboolean.install("JArray_bool", "bool",
                            "__JArray_bool_iterator", module);
    PY_TYPE(JArrayBool) = jarray_jboolean.type_object;

    jarray_jbyte.install("JArray_byte", "byte",
                         "__JArray_byte_iterator", module);
    PY_TYPE(JArrayByte) = jarray_jbyte.type_object;

    jarray_jchar.install("JArray_char", "char",
                         "__JArray_char_iterator", module);
    PY_TYPE(JArrayChar) = jarray_jchar.type_object;

    jarray_jdouble.install("JArray_double", "double",
                           "__JArray_double_iterator", module);
    PY_TYPE(JArrayDouble) = jarray_jdouble.type_object;

    jarray_jfloat.install("JArray_float", "float",
                          "__JArray_float_iterator", module);
    PY_TYPE(JArrayFloat) = jarray_jfloat.type_object;

    jarray_jint.install("JArray_int", "int",
                        "__JArray_int_iterator", module);
    PY_TYPE(JArrayInt) = jarray_jint.type_object;

    jarray_jlong.install("JArray_long", "long",
                         "__JArray_long_iterator", module);
    PY_TYPE(JArrayLong) = jarray_jlong.type_object;

    jarray_jshort.install("JArray_short", "short",
                          "__JArray_short_iterator", module);
    PY_TYPE(JArrayShort) = jarray_jshort.type_object;
}

#endif /* PYTHON */
