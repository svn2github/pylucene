#ifdef _java_generics

#include <jni.h>
#include "JCCEnv.h"
#include "java/lang/reflect/Type.h"
#include "java/lang/Class.h"
#include "JArray.h"

namespace java {
    namespace lang {
        namespace reflect {

            java::lang::Class *Type::class$ = NULL;
            jmethodID *Type::mids$ = NULL;

            jclass Type::initializeClass(bool getOnly)
            {
                if (getOnly)
                    return (jclass) (class$ == NULL ? NULL : class$->this$);
                if (!class$)
                {

                    jclass cls = (jclass) env->findClass("java/lang/reflect/Type");

                    class$ = (java::lang::Class *) new JObject(cls);
                }
                return (jclass) class$->this$;
            }
        }
    }
}

#include "structmember.h"
#include "functions.h"
#include "macros.h"

namespace java {
    namespace lang {
        namespace reflect {
            static PyObject *t_Type_cast_(PyTypeObject *type, PyObject *arg);
            static PyObject *t_Type_instance_(PyTypeObject *type, PyObject *arg);

            static PyMethodDef t_Type__methods_[] = {
                DECLARE_METHOD(t_Type, cast_, METH_O | METH_CLASS),
                DECLARE_METHOD(t_Type, instance_, METH_O | METH_CLASS),
                { NULL, NULL, 0, NULL }
            };

            static PyType_Slot PY_TYPE_SLOTS(Type)[] = {
                { Py_tp_methods, t_Type__methods_ },
                { Py_tp_init, (void *) abstract_init },
                { 0, 0 }
            };

            static PyType_Def *PY_TYPE_BASES(Type)[] = {
                &PY_TYPE_DEF(Object),
                NULL
            };

            DEFINE_TYPE(Type, t_Type, Type);

            static PyObject *t_Type_cast_(PyTypeObject *type, PyObject *arg)
            {
                if (!(arg = castCheck(arg, Type::initializeClass, 1)))
                    return NULL;
                return t_Type::wrap_Object(Type(((t_Type *) arg)->object.this$));
            }
            static PyObject *t_Type_instance_(PyTypeObject *type, PyObject *arg)
            {
                if (!castCheck(arg, Type::initializeClass, 0))
                    Py_RETURN_FALSE;
                Py_RETURN_TRUE;
            }
        }
    }
}

#endif /* _java_generics */
