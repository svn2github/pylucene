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
#include "JCCEnv.h"
#include "java/lang/Object.h"
#include "java/lang/Class.h"
#include "java/lang/Float.h"

namespace java {
    namespace lang {

        enum {
            mid__init_,
            mid_floatValue,
            max_mid
        };

        Class *Float::class$ = NULL;
        jmethodID *Float::_mids = NULL;

        jclass Float::initializeClass(bool getOnly)
        {
            if (getOnly)
                return (jclass) (class$ == NULL ? NULL : class$->this$);
            if (!class$)
            {
                jclass cls = env->findClass("java/lang/Float");

                _mids = new jmethodID[max_mid];
                _mids[mid__init_] = env->getMethodID(cls, "<init>", "(F)V");
                _mids[mid_floatValue] =
                    env->getMethodID(cls, "floatValue", "()F");

                class$ = (Class *) new JObject(cls);
            }

            return (jclass) class$->this$;
        }

        Float::Float(jfloat f) : Object(env->newObject(initializeClass, &_mids, mid__init_, f)) {
        }

        jfloat Float::floatValue() const
        {
            return env->callFloatMethod(this$, _mids[mid_floatValue]);
        }
    }
}


#include "structmember.h"
#include "functions.h"
#include "macros.h"

namespace java {
    namespace lang {

        static PyMethodDef t_Float__methods_[] = {
            { NULL, NULL, 0, NULL }
        };

        static PyType_Slot PY_TYPE_SLOTS(Float)[] = {
            { Py_tp_methods, t_Float__methods_ },
            { Py_tp_init, (void *) abstract_init },
            { 0, 0 }
        };

        static PyType_Def *PY_TYPE_BASES(Float)[] = {
            &PY_TYPE_DEF(Object),
            NULL
        };

        DEFINE_TYPE(Float, t_Float, java::lang::Float);
    }
}
