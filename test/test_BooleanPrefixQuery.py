# ====================================================================
#   Copyright (c) 2004-2008 Open Source Applications Foundation
#
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

from unittest import TestCase, main
from lucene import *


class BooleanPrefixQueryTestCase(TestCase):
    """
    Unit tests ported from Java Lucene
    """

    def testMethod(self):

        directory = RAMDirectory()
        categories = ["food", "foodanddrink",
                      "foodanddrinkandgoodtimes", "food and drink"]

        rw1 = None
        rw2 = None

#        try:
        writer = IndexWriter(directory, WhitespaceAnalyzer(), True)
        for category in categories:
            doc = Document()
            doc.add(Field("category", category,
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            writer.addDocument(doc)

        writer.close()
      
        reader = IndexReader.open(directory)
        query = PrefixQuery(Term("category", "foo"))
      
        rw1 = query.rewrite(reader)
        bq = BooleanQuery()
        bq.add(query, BooleanClause.Occur.MUST)
      
        rw2 = bq.rewrite(reader)
#        except Exception, e:
#            self.fail(str(e))

        bq1 = None
        if BooleanQuery.instance_(rw1):
            bq1 = BooleanQuery.cast_(rw1)
        else:
            self.fail('rewrite')

        bq2 = None
        if BooleanQuery.instance_(rw2):
            bq2 = BooleanQuery.cast_(rw2)
        else:
            self.fail('rewrite')

        self.assertEqual(len(bq1.getClauses()), len(bq2.getClauses()),
                         "Number of Clauses Mismatch")


if __name__ == "__main__":
    import sys, lucene
    lucene.initVM(lucene.CLASSPATH)
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                main()
            except:
                pass
    else:
         main()
