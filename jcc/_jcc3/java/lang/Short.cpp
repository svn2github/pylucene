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
#include "java/lang/Short.h"

namespace java {
    namespace lang {

        enum {
            mid__init_,
            mid_shortValue,
            max_mid
        };

        Class *Short::class$ = NULL;
        jmethodID *Short::_mids = NULL;

        jclass Short::initializeClass(bool getOnly)
        {
            if (getOnly)
                return (jclass) (class$ == NULL ? NULL : class$->this$);
            if (!class$)
            {
                jclass cls = env->findClass("java/lang/Short");

                _mids = new jmethodID[max_mid];
                _mids[mid__init_] = env->getMethodID(cls, "<init>", "(S)V");
                _mids[mid_shortValue] =
                    env->getMethodID(cls, "shortValue", "()S");

                class$ = (Class *) new JObject(cls);
            }

            return (jclass) class$->this$;
        }

        Short::Short(jshort n) : Object(env->newObject(initializeClass, &_mids, mid__init_, n)) {
        }

        jshort Short::shortValue() const
        {
            return env->callShortMethod(this$, _mids[mid_shortValue]);
        }
    }
}


#include "structmember.h"
#include "functions.h"
#include "macros.h"

namespace java {
    namespace lang {

        static PyMethodDef t_Short__methods_[] = {
            { NULL, NULL, 0, NULL }
        };

        static PyType_Slot PY_TYPE_SLOTS(Short)[] = {
            { Py_tp_methods, t_Short__methods_ },
            { Py_tp_init, (void *) abstract_init },
            { 0, 0 }
        };

        static PyType_Def *PY_TYPE_BASES(Short)[] = {
            &PY_TYPE_DEF(Object),
            NULL
        };

        DEFINE_TYPE(Short, t_Short, java::lang::Short);
    }
}
