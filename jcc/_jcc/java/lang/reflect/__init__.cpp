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

#include <Python.h>
#include "macros.h"

namespace java {
    namespace lang {
        namespace reflect {

            extern PyTypeObject Constructor$$Type;
            extern PyTypeObject Method$$Type;
            extern PyTypeObject Modifier$$Type;
            extern PyTypeObject Field$$Type;
#ifdef _java_generics
            extern PyTypeObject Type$$Type;
            extern PyTypeObject ParameterizedType$$Type;
            extern PyTypeObject TypeVariable$$Type;
            extern PyTypeObject GenericArrayType$$Type;
            extern PyTypeObject WildcardType$$Type;
            extern PyTypeObject GenericDeclaration$$Type;
#endif

            void __install__(PyObject *m)
            {
                INSTALL_TYPE(Constructor, m);
                INSTALL_TYPE(Method, m);
                INSTALL_TYPE(Modifier, m);
                INSTALL_TYPE(Field, m);
#ifdef _java_generics
                INSTALL_TYPE(Type, m);
                INSTALL_TYPE(ParameterizedType, m);
                INSTALL_TYPE(TypeVariable, m);
                INSTALL_TYPE(GenericArrayType, m);
                INSTALL_TYPE(WildcardType, m);
                INSTALL_TYPE(GenericDeclaration, m);
#endif
            }
        }
    }
}
