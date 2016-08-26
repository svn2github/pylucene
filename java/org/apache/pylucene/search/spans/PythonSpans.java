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

package org.apache.pylucene.search.spans;

import java.io.IOException;

import org.apache.lucene.search.spans.Spans;
import org.apache.lucene.search.spans.SpanCollector;


public class PythonSpans extends Spans {

    private long pythonObject;

    public PythonSpans()
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

    public native int docID();
    public native int nextDoc()
        throws IOException;
    public native int advance(int target)
        throws IOException;
    public native long cost();

    public native int nextStartPosition();
    public native int startPosition();
    public native int endPosition();
    public native int width();
    public native void collect(SpanCollector collector)
        throws IOException;
    public native float positionsCost();
}
