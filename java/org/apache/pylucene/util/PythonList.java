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

import java.util.List;
import java.util.ListIterator;
import java.util.Collection;
import java.util.Iterator;
import java.lang.reflect.Array;

public class PythonList implements List {

    private long pythonObject;

    public PythonList()
    {
    }

    public void pythonExtension(long pythonObject)
    {
        this.pythonObject = pythonObject;
    }
    public long pythonExtension()
    {
        return this.pythonObject;
    }

    public void finalize()
        throws Throwable
    {
        pythonDecRef();
    }

    public native void pythonDecRef();
  
    @Override
    public native boolean add(Object obj);
    @Override
    public native void add(int index, Object obj);
    @Override
    public native boolean addAll(Collection c);
    @Override
    public native boolean addAll(int index, Collection c);
    @Override
    public native void clear();
    @Override
    public native boolean contains(Object obj);
    @Override
    public native boolean containsAll(Collection c);
    @Override
    public native boolean equals(Object obj);
    @Override
    public native Object get(int index);
    // public native int hashCode();
    @Override
    public native int indexOf(Object obj);
    @Override
    public native boolean isEmpty();
    @Override
    public native Iterator iterator();
    @Override
    public native int lastIndexOf(Object obj);

    public native ListIterator listIterator(int index); 
    @Override
    public ListIterator listIterator()
    {
        return listIterator(0);
    }

    private native Object removeAt(int index);
    @Override
    public Object remove(int index)
        throws IndexOutOfBoundsException
    { 
        if (index < 0 || index >= this.size())
            throw new IndexOutOfBoundsException(); 

        return removeAt(index);
    }
    
    private native boolean removeObject(Object obj);
    @Override
    public boolean remove(Object obj)
    {
        return removeObject(obj);
    }
    
    @Override
    public native boolean removeAll(Collection c);
    @Override
    public native boolean retainAll(Collection c);
    @Override
    public native Object set(int index, Object obj);
    @Override
    public native int size();
    
    private native List subListChecked(int fromIndex, int toIndex);     
    @Override
    public List subList(int fromIndex, int toIndex) 
        throws IndexOutOfBoundsException, IllegalArgumentException
    { 
        if (fromIndex < 0 || toIndex >= size() || fromIndex > toIndex)
            throw new IndexOutOfBoundsException(); 

        return subListChecked(fromIndex, toIndex);
    }
    
    public native Object[] toArray();

    @Override
    public Object[] toArray(Object[] a)
    {
        Object[] array = toArray();
        
        if (a.length < array.length)
            a = (Object[]) Array.newInstance(a.getClass().getComponentType(),
                                             array.length);

        System.arraycopy(array, 0, a, 0, array.length);

        return a;
    }
}
