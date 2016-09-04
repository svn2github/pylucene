/* ====================================================================
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
 * ====================================================================
 */

package org.apache.pylucene.util;

import java.util.ListIterator;

public class PythonListIterator extends PythonIterator implements ListIterator {
    @Override
    public native boolean hasPrevious();
    @Override
    public native Object previous();
    
    @Override
    public native int nextIndex();
    @Override
    public native int previousIndex();
    
    @Override
    public native void set(Object obj);    
    @Override
    public native void add(Object obj);
    @Override
    public native void remove();
}
