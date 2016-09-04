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

package org.apache.pylucene.store;

import java.io.IOException;
import org.apache.lucene.store.BufferedIndexInput;
import org.apache.lucene.store.IOContext;


public class PythonIndexInput extends BufferedIndexInput {

    private long pythonObject;

    public PythonIndexInput(String resourceDesc)
    {
        super(resourceDesc);
    }

    public PythonIndexInput(String resourceDesc, int bufferSize)
    {
        super(resourceDesc, bufferSize);
    }

    public PythonIndexInput(String resourceDesc, IOContext context)
    {
        super(resourceDesc, context);
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
    public native PythonIndexInput clone();
    @Override
    public native long length();
    @Override
    public native void close()
        throws IOException;
    @Override
    public native void seekInternal(long pos)
        throws IOException;

    public native byte[] readInternal(int length, long pos)
        throws IOException;

    @Override
    protected void readInternal(byte[] b, int offset, int length)
        throws IOException
    {
        byte[] data = readInternal(length, getFilePointer());
        System.arraycopy(data, 0, b, offset, data.length);
    }
}
