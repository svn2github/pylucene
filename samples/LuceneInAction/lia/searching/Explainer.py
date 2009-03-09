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

import os

from lucene import \
     SimpleAnalyzer, Document, QueryParser, Explanation, \
     IndexSearcher, FSDirectory, Hit


class Explainer(object):

    def main(cls, argv):

        if len(argv) != 3:
            print "Usage: Explainer <index dir> <query>"

        else:
            indexDir = argv[1]
            queryExpression = argv[2]

            directory = FSDirectory.getDirectory(indexDir, False)

            query = QueryParser("contents",
                                SimpleAnalyzer()).parse(queryExpression)

            print "Query:", queryExpression

            searcher = IndexSearcher(directory)
            hits = searcher.search(query)

            for hit in hits:
                hit = Hit.cast_(hit)
                doc = hit.getDocument()
                id = hit.getId()
                explanation = searcher.explain(query, id)
                print "----------"
                print doc["title"].encode('utf-8')
                print explanation

    main = classmethod(main)


if __name__ == "__main__":
    import sys
    Explainer.main(sys.argv)
