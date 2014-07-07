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
#   (originally based on the Java counterpart from
#    package org.apache.lucene.facet.example.simple
#    later updated to new Facet API)
# ====================================================================

usage = """
  usage: python FacetExample.py [index | simple | drilldown]
  where
    'index' => create index for faceted search
    'simple'  => run simple faceted search
    'drilldown' => run faceted search with drilldown
"""

INDEX_DIR = "FacetExample.Index"
TAXONOMY_DIR = "FacetExample.Taxonomy"

import os, sys, lucene

from java.io import File
from java.lang import System
from java.text import DecimalFormat
from java.util import Arrays

from org.apache.lucene.util import Version
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.search import IndexSearcher, TermQuery, MatchAllDocsQuery
from org.apache.lucene.store import FSDirectory, SimpleFSDirectory
from org.apache.lucene.index import (IndexWriter, IndexReader,
                                     DirectoryReader, Term,
                                     IndexWriterConfig)
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.facet import DrillSideways, DrillDownQuery
from org.apache.lucene.facet import (Facets, FacetField, FacetResult,
                                     FacetsConfig, FacetsCollector)
from org.apache.lucene.facet.taxonomy import FastTaxonomyFacetCounts
from org.apache.lucene.facet.taxonomy.directory import (DirectoryTaxonomyWriter,
                                                        DirectoryTaxonomyReader)

# -----------------------------------------------------------------------------
# SimpleUtils:
# Documents title field
TITLE = "title"
TEXT = "text"
docTexts = [
    "The white car is the one I want.",           # doc nr.0
    "The white dog does not belong to anyone."    # doc nr.1
]

# sample documents titles (for the title field).
docTitles = [
    "white car",  # doc nr.0
    "white dog",  # doc nr.1
]

# Authors: author[n] ==  Author of n-th document
# example for simple, single-value facet
authors = [
    "Bob",   # doc nr.0
    "Lisa"   # doc nr.1
]

# Categories: categories[D][N] == category-path no. N for document no. D.
# example for hierarchical multi-value facet
categories = [
    [["root","a","f1"], ["root","a","f2"]], # doc nr.0
    [["root","a","f1"], ["root","a","f3"]]  # doc nr.1
]

# samples for (drilldown) search
searchValues = ['white', 'car']
drilldownCategories = [["root","a","f1"],  ["root","a","f2"]]

# -----------------------------------------------------------------------------
# Sample indexer creates an index, and adds to it sample documents and facets.

class SimpleIndexer(object):

    def index (cls, indexDir, taxoDir, facets_config):
        """Create an index, and adds to it sample documents and facets.
        indexDir Directory in which the index should be created.
        taxoDir Directory in which the taxonomy index should be created.
        """
        # create and open an index writer
        config = IndexWriterConfig(Version.LUCENE_48,
                                   WhitespaceAnalyzer(Version.LUCENE_48))
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        iw = IndexWriter(indexDir, config)
        # create and open a taxonomy writer
        taxo = DirectoryTaxonomyWriter(taxoDir, IndexWriterConfig.OpenMode.CREATE)
        # loop over sample documents
        nDocsAdded = 0
        nFacetsAdded = 0
        for docNum in range(len(docTexts)):
            # create a plain Lucene document and add some regular Lucene fields to it
            doc = Document()
            doc.add(TextField(TITLE, docTitles[docNum], Field.Store.YES))
            doc.add(TextField(TEXT, docTexts[docNum], Field.Store.NO))
            # obtain the sample facets for current document
            facets = categories[docNum]
            author = authors[docNum]
            # ... and use the FacetField class for adding facet fields to
            # the Lucene document (and via FacetsConfig to the taxonomy index)
            doc.add(FacetField("Author", author))
            for f in facets:
                doc.add(FacetField("Categories", f))
            # finally add the document to the index
            iw.addDocument(facets_config.build(taxo, doc))
            nDocsAdded += 1

        # close the taxonomy index and the index - all modifications are
        # now safely in the provided directories: indexDir and taxoDir.
        iw.close()
        taxo.close()
        print "Indexed %d documents with facets." % nDocsAdded

    index = classmethod(index)

# -----------------------------------------------------------------------------
# SimpleSearcer searches index with facets.

class SimpleSearcher(object):

    def searchWithFacets(cls, indexReader, taxoReader, facets_config):
        """
        Search an index with facets.
        return a list of FacetResult instances
        """
        # MatchAllDocsQuery is for "browsing" (counts facets for all non-deleted docs in the index)
        query = MatchAllDocsQuery()
        return cls.searchWithQuery(query, indexReader, taxoReader, facets_config)

    def searchWithTerm(cls, query, indexReader, taxoReader, facets_config):
        """
        Search an index with facets by using simple term query
        return a list of FacetResult instances
        """
        query = TermQuery(Term(TEXT, query))
        return cls.searchWithQuery(query, indexReader, taxoReader, facets_config)

    def searchWithQuery(cls, query, indexReader, taxoReader, facets_config):
        """
        Search an index with facets for a given query
        return a list of FacetResult instances
        """
        # prepare searcher to search against
        searcher = IndexSearcher(indexReader)
        # create a FacetsCollector to use in our facetted search:
        facets_collector = FacetsCollector()
        FacetsCollector.search(searcher, query, 10, facets_collector)
        # Count both "Categories" and "Author" dimensions
        facets = FastTaxonomyFacetCounts(taxoReader, facets_config, facets_collector)
        results = []

        facet_result = facets.getTopChildren(10, "Categories")
        if facet_result:
            results.append(facet_result)
            print  "Categories: ", facet_result.childCount
            for  lv in facet_result.labelValues:
                print " '%s' (%s)"  % (lv.label, lv.value)

        facet_result = facets.getTopChildren(10, "Categories", "root", "a")
        if facet_result:
            results.append(facet_result)
            print  "Root-a-Categories: ", facet_result.childCount
            for  lv in facet_result.labelValues:
                print " '%s' (%s)"  % (lv.label, lv.value)

        facet_result = facets.getTopChildren(10, "Author")
        if facet_result:
            results.append(facet_result)
            print  "Author: ", facet_result.childCount
            for  lv in facet_result.labelValues:
                print " '%s' (%s)"  % (lv.label, lv.value)

        return results

    def searchWithDrillDown(cls, drilldownCategory, indexReader, taxoReader, facets_config):
        """
        Search an index with facets drill-down.
        return a list of FacetResult instances
        """
        #  User drills down on 'Categories' "root/a/f1" and we return facets for 'Author'
        searcher = IndexSearcher(indexReader)
        #  Passing no baseQuery means we drill down on all documents ("browse only"):
        query =  DrillDownQuery(facets_config)
        # Now user drills down on Publish Date/2010:
        query.add("Categories",  drilldownCategory)
        facets_collector = FacetsCollector()
        FacetsCollector.search(searcher, query, 10, facets_collector)
        # Retrieve results
        facets =  FastTaxonomyFacetCounts(taxoReader, facets_config, facets_collector)
        facet_result = facets.getTopChildren(10, "Author")
        print  "Author: ", facet_result.childCount
        for  lv in facet_result.labelValues:
            print " '%s' (%s)"  % (lv.label, lv.value)

        return facet_result


    searchWithFacets = classmethod(searchWithFacets)
    searchWithTerm = classmethod(searchWithTerm)
    searchWithQuery = classmethod(searchWithQuery)
    searchWithDrillDown = classmethod(searchWithDrillDown)


# -----------------------------------------------------------------------------

class FacetExample(object):

    def __init__(self, directory):
        self.directory = directory
        # create Directories for the search index and for the taxonomy index
        # in RAM or on Disc
        #indexDir = RAMDirectory()
        #taxoDir = RAMDirectory()
        self.indexDir = FSDirectory.open(File(os.path.join(self.directory,
                                                           INDEX_DIR)))
        self.taxoDir = FSDirectory.open(File(os.path.join(self.directory,
                                                          TAXONOMY_DIR)))
        # FacetConfig
        self.facets_config = FacetsConfig()
        self.facets_config.setHierarchical("Categories", True)
        self.facets_config.setMultiValued("Categories", True)


    def createIndex(self):
        # index the sample documents
        SimpleIndexer.index(self.indexDir, self.taxoDir, self.facets_config)

    def runSimple(self):
        # open readers
        taxo = DirectoryTaxonomyReader(self.taxoDir)
        indexReader = DirectoryReader.open(self.indexDir)

        for term in searchValues:
            print  "\nsearch by term '%s' ..." % term
            facetRes = SimpleSearcher.searchWithTerm(term, indexReader, taxo,
                                                       self.facets_config)
        print  "\nsearch all documents  ..."
        facetRes = SimpleSearcher.searchWithFacets(indexReader, taxo,
                                                   self.facets_config)
        # close readers
        taxo.close()
        indexReader.close()
        # return result
        return facetRes

    def runDrillDown(self):
        # open readers
        taxo = DirectoryTaxonomyReader(self.taxoDir)
        indexReader = DirectoryReader.open(self.indexDir)

        for drilldown in drilldownCategories:
            print "search with drilldown: %s" %  '/'.join(drilldown)
            facetRes = SimpleSearcher.searchWithDrillDown(drilldown, indexReader,
                                                          taxo, self.facets_config)
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
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    FacetExample.main(sys.argv)
