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

package org.apache.pylucene.search;

import java.io.IOException;

import org.apache.lucene.index.LeafReaderContext;
import org.apache.lucene.search.SimpleCollector;
import org.apache.lucene.search.Scorer;


public class PythonSimpleCollector extends SimpleCollector {

    private long pythonObject;

    public PythonSimpleCollector()
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

    protected Scorer scorer;

    public void setScorer(Scorer scorer)
        throws IOException
    {
        this.scorer = scorer;
    }

    public void collect(int doc)
        throws IOException
    {
        collect(doc, scorer.score());
    }

    public native void pythonDecRef();

    public native void collect(int doc, float score)
        throws IOException;

    @Override
    public native void doSetNextReader(LeafReaderContext context)
        throws IOException;

    @Override
    public native boolean needsScores();
}
