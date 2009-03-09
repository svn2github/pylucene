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

from lucene import \
    PythonQueryParser, PythonMultiFieldQueryParser, \
    PhraseQuery, RangeQuery, SpanNearQuery, SpanTermQuery, \
    Term, PhraseQuery

from lia.extsearch.queryparser.NumberUtils import NumberUtils

#
# A QueryParser extension
#

class CustomQueryParser(PythonQueryParser):

    def __init__(self, field, analyzer):
        super(CustomQueryParser, self).__init__(field, analyzer)

    def getFuzzyQuery(self, field, termText, minSimilarity):
        raise AssertionError, "Fuzzy queries not allowed"

    def getWildcardQuery(self, field, termText):
        raise AssertionError, "Wildcard queries not allowed"

    #
    # Special handling for the "id" field, pads each part
    # to match how it was indexed.
    #
    def getRangeQuery(self, field, part1, part2, inclusive):

        if field == "id":

            num1 = int(part1)
            num2 = int(part2)

            return RangeQuery(Term(field, NumberUtils.pad(num1)),
                              Term(field, NumberUtils.pad(num2)),
                              inclusive)

        if field == "special":
            print part1, "->", part2

            if part1 == '*':
                t1 = None
            else:
                t1 = Term("field", part1)

            if part2 == '*':
                t2 = None
            else:
                t2 = Term("field", part2)

            return RangeQuery(t1, t2, inclusive)

        return super(CustomQueryParser,
                     self).getRangeQuery(field, part1, part2, inclusive)

    #
    # Replace PhraseQuery with SpanNearQuery to force in-order
    # phrase matching rather than reverse.
    #
    def getFieldQuery(self, field, queryText, slop=None):

        if slop is None:
            return super(CustomQueryParser,
                         self).getFieldQuery(field, queryText)

        # let QueryParser's implementation do the analysis
        orig = super(CustomQueryParser,
                     self).getFieldQuery(field, queryText, slop)

        if not PhraseQuery.instance_(orig):
            return orig

        pq = PhraseQuery.cast_(orig)
        clauses = [SpanTermQuery(term) for term in pq.getTerms()]

        return SpanNearQuery(clauses, slop, True);



class MultiFieldCustomQueryParser(PythonMultiFieldQueryParser):

    def __init__(self, fields, analyzer):
        super(MultiFieldCustomQueryParser, self).__init__(fields, analyzer)

    def getFuzzyQuery(self, super, field, termText, minSimilarity):
        raise AssertionError, "Fuzzy queries not allowed"

    def getWildcardQuery(self, super, field, termText):
        raise AssertionError, "Wildcard queries not allowed"

    #
    # Special handling for the "id" field, pads each part
    # to match how it was indexed.
    #
    def getRangeQuery(self, field, part1, part2, inclusive):

        if field == "id":

            num1 = int(part1)
            num2 = int(part2)

            return RangeQuery(Term(field, NumberUtils.pad(num1)),
                              Term(field, NumberUtils.pad(num2)),
                              inclusive)

        if field == "special":
            print part1, "->", part2

            if part1 == '*':
                t1 = None
            else:
                t1 = Term("field", part1)

            if part2 == '*':
                t2 = None
            else:
                t2 = Term("field", part2)

            return RangeQuery(t1, t2, inclusive)

        return super(CustomQueryParser,
                     self).getRangeQuery(field, part1, part2, inclusive)

    #
    # Replace PhraseQuery with SpanNearQuery to force in-order
    # phrase matching rather than reverse.
    #
    def getFieldQuery(self, field, queryText, slop=None):

        if slop is None:
            return super(CustomQueryParser,
                         self).getFieldQuery(field, queryText)

        # let QueryParser's implementation do the analysis
        orig = super(CustomQueryParser,
                     self).getFieldQuery(field, queryText, slop)

        if not PhraseQuery.instance_(orig):
            return orig

        pq = PhraseQuery.cast_(orig)
        clauses = [SpanTermQuery(term) for term in pq.getTerms()]

        return SpanNearQuery(clauses, slop, True);
