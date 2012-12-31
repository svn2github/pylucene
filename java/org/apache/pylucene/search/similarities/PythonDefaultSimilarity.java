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

package org.apache.pylucene.search.similarities;

import org.apache.lucene.search.Explanation;
import org.apache.lucene.search.CollectionStatistics;
import org.apache.lucene.search.TermStatistics;
import org.apache.lucene.search.similarities.DefaultSimilarity;
import org.apache.lucene.index.FieldInvertState;


public class PythonDefaultSimilarity extends DefaultSimilarity {

    private long pythonObject;

    public PythonDefaultSimilarity()
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

    public native float queryNorm(float sumOfSquaredWeights);
    public native float coord(int overlap, int maxOverlap);
    public native float lengthNorm(FieldInvertState state);
    public native float tf(float freq);
    public native float sloppyFreq(int distance);
    public native float idf(long docFreq, long numDocs);

    public native Explanation idfExplain(CollectionStatistics collectionStats,
                                         TermStatistics[] stats);
}
