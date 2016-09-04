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

import org.apache.lucene.index.PostingsEnum;
import org.apache.lucene.index.Term;

import org.apache.lucene.search.spans.SpanCollector;


public class PythonSpanCollector implements SpanCollector {

    private long pythonObject;

    public PythonSpanCollector()
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
    public native void collectLeaf(PostingsEnum postings, int position,
                                   Term term)
        throws IOException;

    @Override
    public native void reset();
}
