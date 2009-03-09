# ====================================================================
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# ====================================================================

from math import sqrt
from lucene import SortField, Term, IndexReader, \
    PythonSortComparatorSource, PythonScoreDocComparator, Double

#
# A SortComparatorSource implementation
#

class DistanceComparatorSource(PythonSortComparatorSource):

    def __init__(self, x, y):
        super(DistanceComparatorSource, self).__init__()
        self.x = x
        self.y = y

    def newComparator(self, reader, fieldName):

        #
        # A ScoreDocComparator implementation
        # 
        class DistanceScoreDocLookupComparator(PythonScoreDocComparator):

            def __init__(self, reader, fieldName, x, y):
                super(DistanceScoreDocLookupComparator, self).__init__()
                enumerator = reader.terms(Term(fieldName, ""))
                self.distances = distances = [0.0] * reader.numDocs()

                if reader.numDocs() > 0:
                    termDocs = reader.termDocs()
                    try:
                        while True:
                            term = enumerator.term()
                            if term is None:
                                raise RuntimeError, "no terms in field %s" %(fieldName)
                            if term.field() != fieldName:
                                break
                            
                            termDocs.seek(enumerator)
                            while termDocs.next():
                                xy = term.text().split(',')
                                deltax = int(xy[0]) - x
                                deltay = int(xy[1]) - y

                                distances[termDocs.doc()] = sqrt(deltax ** 2 +
                                                                 deltay ** 2)
            
                            if not enumerator.next():
                                break
                    finally:
                        termDocs.close()

            def compare(self, i, j):

                if self.distances[i.doc] < self.distances[j.doc]:
                    return -1
                if self.distances[i.doc] > self.distances[j.doc]:
                    return 1
                return 0

            def sortValue(self, i):

                return Double(self.distances[i.doc])

            def sortType(self):

                return SortField.FLOAT

        return DistanceScoreDocLookupComparator(reader, fieldName,
                                                self.x, self.y)

    def __str__(self):

        return "Distance from ("+x+","+y+")"
