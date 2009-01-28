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

import org.apache.lucene.search.Similarity;
import org.apache.lucene.search.SimilarityDelegator;
import org.apache.lucene.search.Searcher;
import org.apache.lucene.index.Term;


public class PythonSimilarityDelegator extends SimilarityDelegator {

    private long pythonObject;

    public PythonSimilarityDelegator(Similarity delegee)
    {
        super(delegee);
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
    public native float lengthNorm(String fieldName, int numTokens);
    public native float queryNorm(float sumOfSquaredWeights);
    public native float tf(float freq);
    public native float sloppyFreq(int distance);
    public native float idf(int docFreq, int numDocs);
    public native float coord(int overlap, int maxOverlap);
    public native float scorePayload(String fieldName, byte[] payload,
                                     int offset, int length);
}
