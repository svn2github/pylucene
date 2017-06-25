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
#include "java/lang/Exception.h"

namespace java {
    namespace lang {

        enum {
            max_mid
        };

        Class *Exception::class$ = NULL;
        jmethodID *Exception::_mids = NULL;

        jclass Exception::initializeClass(bool getOnly)
        {
            if (getOnly)
                return (jclass) (class$ == NULL ? NULL : class$->this$);
            if (!class$)
            {
                jclass cls = env->findClass("java/lang/Exception");

                class$ = (Class *) new JObject(cls);
            }

            return (jclass) class$->this$;
        }
    }
}


#include "structmember.h"
#include "functions.h"
#include "macros.h"

namespace java {
    namespace lang {

        static PyMethodDef t_Exception__methods_[] = {
            { NULL, NULL, 0, NULL }
        };

        static PyType_Slot PY_TYPE_SLOTS(Exception)[] = {
            { Py_tp_methods, t_Exception__methods_ },
            { Py_tp_init, (void *) abstract_init },
            { 0, 0 }
        };

        static PyType_Def *PY_TYPE_BASES(Exception)[] = {
            &PY_TYPE_DEF(Throwable),
            NULL
        };

        DEFINE_TYPE(Exception, t_Exception, java::lang::Exception);
    }
}
