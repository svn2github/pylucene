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
import org.apache.lucene.search.similarities.ClassicSimilarity;
import org.apache.lucene.index.FieldInvertState;


public class PythonClassicSimilarity extends ClassicSimilarity {

    private long pythonObject;

    public PythonClassicSimilarity()
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
    public native float queryNorm(float sumOfSquaredWeights);
    @Override
    public native float coord(int overlap, int maxOverlap);
    @Override
    public native float lengthNorm(FieldInvertState state);
    @Override
    public native float tf(float freq);
    @Override
    public native float sloppyFreq(int distance);
    @Override
    public native float idf(long docFreq, long numDocs);
    @Override
    public native Explanation idfExplain(CollectionStatistics collectionStats,
                                         TermStatistics[] stats);
}
