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
#
# Author: Thomas Koch
#
# FacetExample.py - a simple Facet example for PyLucene
#   (based on the Java counterpart from
#    package org.apache.lucene.facet.example.simple)
# ====================================================================

usage = """
  usage: python FacetExample.py [index | simple | drilldown]
  where
    'index' => create index for faceted search
    'simple'  => run simple faceted search
    'drilldown' => run faceted search with drilldown
"""

import os, sys, lucene

from lucene import FSDirectory, SimpleFSDirectory, Document, Field,\
    IndexWriter, IndexSearcher, IndexReader, IndexWriterConfig, \
    WhitespaceAnalyzer, StandardAnalyzer, \
    MatchAllDocsQuery, Sort, SortField, DecimalFormat, System, File, \
    TopFieldCollector, QueryParser, Version, BooleanQuery, BooleanClause, \
    DirectoryTaxonomyWriter, DirectoryTaxonomyReader, \
    CategoryDocumentBuilder, CategoryPath


# -----------------------------------------------------------------------------
# SimpleUtils:
# Documents title field
TITLE = "title"
TEXT = "text";

docTexts = [
    "the white car is the one I want.",
    "the white dog does not belong to anyone.",
]

# sample documents titles (for the title field).

docTitles = [
    "white car",  # doc nr.0
    "white dog",  # doc nr.1
]

# Categories: categories[D][N] == category-path no. N for document no. D.

categories = [
    [["root","a","f1"], ["root","a","f2"]], # doc nr.0
    [["root","a","f1"], ["root","a","f3"]]  # doc nr.1
]


def createCategoryPath(strList):
    """create CategoryPath and initialize with categories
     from given string list (python helper method)
     """
    cp = CategoryPath()
    for s in strList:
        cp.add(s)
    return cp


# -----------------------------------------------------------------------------
# port of org.apache.lucene.facet.example.simple from java to python
# Sample indexer creates an index, and adds to it sample documents and facets.

class SimpleIndexer(object):

    def index (cls, indexDir, taxoDir):
        """Create an index, and adds to it sample documents and facets.
        indexDir Directory in which the index should be created.
        taxoDir Directory in which the taxonomy index should be created.
        """
        # create and open an index writer
        ver = lucene.Version.LUCENE_35
        config = IndexWriterConfig(ver, WhitespaceAnalyzer(ver))
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        iw = IndexWriter(indexDir, config)
        # create and open a taxonomy writer
        taxo = DirectoryTaxonomyWriter(taxoDir, IndexWriterConfig.OpenMode.CREATE)
        # loop over sample documents
        nDocsAdded = 0
        nFacetsAdded = 0
        for docNum in range(len(docTexts)):
            # obtain the sample facets for current document
            facets = categories[docNum]
            facetList = [ createCategoryPath(f) for f in facets]
            # NOTE: setCategoryPaths() requires an Iterable, so need to convert the
            #       Python list in order to to pass a proper argument to setCategoryPaths.
            #       We use java.util.Arrays (via JCC) to create a Java List.
            # see http://docs.oracle.com/javase/1.5.0/docs/api/java/util/Arrays.html#asList(T...)
            facetList = lucene.Arrays.asList(facetList)
            # NOTE: we could use lucene.collections here as well in order to convert our
            # Python list to a Java based list using the JavaList class (JavaList implements
            # java.util.List around a Python list instance it wraps):
            #  from lucene.collections import JavaList
            #  facetList = JavaList(facetList)

            # we do not alter indexing parameters
            # a category document builder will add the categories to a document once build() is called
            categoryDocBuilder = CategoryDocumentBuilder(taxo).setCategoryPaths(facetList)

            # create a plain Lucene document and add some regular Lucene fields to it
            doc = Document()
            doc.add(Field(TITLE, docTitles[docNum], Field.Store.YES, Field.Index.ANALYZED))
            doc.add(Field(TEXT, docTexts[docNum], Field.Store.NO, Field.Index.ANALYZED))

            # invoke the category document builder for adding categories to the document and,
            # as required, to the taxonomy index
            categoryDocBuilder.build(doc)
            # finally add the document to the index
            iw.addDocument(doc)
            nDocsAdded +=1
            nFacetsAdded += facetList.size()
        # end for

        # commit changes.
        # we commit changes to the taxonomy index prior to committing them to the search index.
        # this is important, so that all facets referred to by documents in the search index
        # will indeed exist in the taxonomy index.
        taxo.commit()
        iw.commit()

        # close the taxonomy index and the index - all modifications are
        # now safely in the provided directories: indexDir and taxoDir.
        taxo.close()
        iw.close()
        print "Indexed %d documents with overall %d facets." % (nDocsAdded,nFacetsAdded)

    index = classmethod(index)

# -----------------------------------------------------------------------------
# port of org.apache.lucene.facet.example.simple from java to python
# SimpleSearcer searches index with facets.

from lucene import (Query, Term, TermQuery, TopScoreDocCollector,
                    MultiCollector,
                    DefaultFacetIndexingParams, FacetIndexingParams,
                    DrillDown, FacetsCollector, CountFacetRequest,
                    FacetRequest, FacetSearchParams,FacetResult,
                    FacetResultNode)


class SimpleSearcher(object):

    def searchWithFacets(cls, indexReader, taxoReader):
        """
        Search an index with facets.
        returns a List<FacetResult>
        """
        facetRequest = CountFacetRequest(createCategoryPath(["root","a"]), 10)
        return cls.searchWithRequest(indexReader, taxoReader, None, facetRequest)

    def searchWithRequest(cls, indexReader, taxoReader, indexingParams, facetRequest):
        """
        Search an index with facets for given facet requests.
        returns a List<FacetResult>
        """
        query = TermQuery(Term(TEXT, "white"))
        return cls.searchWithRequestAndQuery(query, indexReader, taxoReader,
                                         indexingParams, facetRequest)

    def searchWithRequestAndQuery(cls, query, indexReader, taxoReader,
                                  indexingParams, facetRequest):
        """
        Search an index with facets for given query and facet requests.
        returns a List<FacetResult>
        """
        # prepare searcher to search against
        searcher = IndexSearcher(indexReader)
        # collect matching documents into a collector
        topDocsCollector = TopScoreDocCollector.create(10, True)
        if not indexingParams:
            indexingParams = DefaultFacetIndexingParams()

        # Faceted search parameters indicate which facets are we interested in
        facetSearchParams = FacetSearchParams(indexingParams)
        # Add the facet request of interest to the search params
        facetSearchParams.addFacetRequest(facetRequest)
        facetsCollector = FacetsCollector(facetSearchParams, indexReader, taxoReader)
        # perform documents search and facets accumulation
        searcher.search(query, MultiCollector.wrap([topDocsCollector, facetsCollector]))
        # Obtain facets results and print them
        res = facetsCollector.getFacetResults()
        i = 0
        for facetResult in res:
            print "Result #%d has %d descendants" % (i, facetResult.getNumValidDescendants())
            print "Result #%d : %s" % (i, facetResult)
            i += 1

        return res


    def searchWithDrillDown(cls, indexReader, taxoReader):
        """
        Search an index with facets drill-down.
        returns a List<FacetResult>
        """
        # base query the user is interested in
        baseQuery = TermQuery(Term(TEXT, "white"))
        # facet of interest
        facetRequest = CountFacetRequest(createCategoryPath(["root","a"]), 10)
        # initial search - all docs matching the base query will contribute to the accumulation
        res1 = cls.searchWithRequest(indexReader, taxoReader, None, facetRequest)
        # a single result (because there was a single request)
        fres = res1.get(0)
        # assume the user is interested in the second sub-result
        # (just take the second sub-result returned by the iterator - we know there are 3 results!)
        subResults = fres.getFacetResultNode().getSubResults()
        # NOTE: .getSubResults() yields an "Iterable<? extends FacetResultNode>:"
        #  the elements of this iterator are of type Object and need to be casted to
        #  FacetResultNode by calling FacetResultNode.cast_(obj) first
        resIterator = subResults.iterator()
        resIterator.next() # skip first result
        resultNode = resIterator.next()
        resultNode = FacetResultNode.cast_(resultNode)
        categoryOfInterest = resultNode.getLabel()
        # drill-down preparation: turn the base query into a drill-down query for the category of interest
        query2 = DrillDown.query(baseQuery, [categoryOfInterest,])
        # that's it - search with the new query and we're done!
        # only documents both matching the base query AND containing the
        # category of interest will contribute to the new accumulation
        return cls.searchWithRequestAndQuery(query2, indexReader, taxoReader,
                                             None, facetRequest)


    searchWithFacets = classmethod(searchWithFacets)
    searchWithRequest = classmethod(searchWithRequest)
    searchWithRequestAndQuery = classmethod(searchWithRequestAndQuery)
    searchWithDrillDown = classmethod(searchWithDrillDown)


# -----------------------------------------------------------------------------

class FacetExample(object):

    def __init__(self, directory):
        self.directory = directory
        # create Directories for the search index and for the taxonomy index
        # in RAM or on Disc
        #indexDir = RAMDirectory()
        #taxoDir = RAMDirectory()
        self.indexDir = FSDirectory.open(File(os.path.join(self.directory,'Index')))
        self.taxoDir = FSDirectory.open(File(os.path.join(self.directory,'Taxonomy')))

    def createIndex(self):
        # index the sample documents
        SimpleIndexer.index(self.indexDir, self.taxoDir)

    def runSimple(self):
        # open readers
        taxo = DirectoryTaxonomyReader(self.taxoDir)
        indexReader = IndexReader.open(self.indexDir, True)
        # returns List<FacetResult>
        facetRes = SimpleSearcher.searchWithFacets(indexReader, taxo)
        # close readers
        taxo.close()
        indexReader.close()
        # return result
        return facetRes

    def runDrillDown(self):
        # open readers
        taxo = DirectoryTaxonomyReader(self.taxoDir)
        indexReader = IndexReader.open(self.indexDir, True)
        facetRes = SimpleSearcher.searchWithDrillDown(indexReader, taxo)
        # close readers
        taxo.close()
        indexReader.close()
        # return result
        return facetRes

    def main(cls, argv):
        baseDir = os.path.dirname(os.path.abspath(argv[0]))
        if len(argv) > 1:
            index = simple = drilldown = False
            for arg in argv[1:]:
                if arg == "index":
                    index = True
                elif arg == "simple":
                    simple = True
                elif arg == "drilldown":
                    drilldown = True
                else:
                    sys.exit(usage+"\nunknown argument: %s" % arg)
        else:
            index = simple = True
            drilldown = False

        example = FacetExample(baseDir)
        if index:
            example.createIndex()
        if simple:
            example.runSimple()
        if drilldown:
            example.runDrillDown()

    main = classmethod(main)



if __name__ == '__main__':
    lucene.initVM()
    FacetExample.main(sys.argv)
