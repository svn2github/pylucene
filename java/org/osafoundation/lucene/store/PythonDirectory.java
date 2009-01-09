/* ====================================================================
 *   Copyright (c) 2004-2008 Open Source Applications Foundation
 *
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

package org.osafoundation.lucene.store;

import org.apache.lucene.store.Directory;
import org.apache.lucene.store.IndexInput;
import org.apache.lucene.store.IndexOutput;
import org.apache.lucene.store.Lock;


public class PythonDirectory extends Directory {

    private long pythonObject;

    public PythonDirectory()
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
    public native void close();
    public native IndexOutput createOutput(String name);
    public native void deleteFile(String name);
    public native boolean fileExists(String name);
    public native long fileLength(String name);
    public native long fileModified(String name);
    public native String[] list();
    public native Lock makeLock(String name);
    public native IndexInput openInput(String name);
    public native IndexInput openInput(String name, int bufferSize);
    public native void touchFile(String name);

    /* no longer implemented, deprecated in Lucene 2.1 */
    public void renameFile(String from, String to)
    {
    }
}
