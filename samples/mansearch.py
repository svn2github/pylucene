# ====================================================================
# Copyright (c) 2004-2007 Open Source Applications Foundation.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions: 
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software. 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
# ====================================================================
#
# Author: Erik Hatcher
#
# to query the index generated with manindex.py
#  python mansearch.py <query>
# by default, the index is stored in 'pages', which can be overriden with
# the MANDEX environment variable
# ====================================================================


import sys, os

from string import Template
from datetime import datetime
from getopt import getopt, GetoptError

from lucene import \
     Document, IndexSearcher, FSDirectory, QueryParser, StandardAnalyzer, \
     Hit, Field, initVM, CLASSPATH

if __name__ == '__main__':
    initVM(CLASSPATH)

def usage():
    print sys.argv[0], "[--format=<format string>] [--index=<index dir>] [--stats] <query...>"
    print "default index is found from MANDEX environment variable"

try:
    options, args = getopt(sys.argv[1:], '', ['format=', 'index=', 'stats'])
except GetoptError:
    usage()
    sys.exit(2)


format = "#name"
indexDir = os.environ.get('MANDEX') or 'pages'
stats = False
for o, a in options:
    if o == "--format":
        format = a
    elif o == "--index":
        indexDir = a
    elif o == "--stats":
        stats = True


class CustomTemplate(Template):
    delimiter = '#'

template = CustomTemplate(format)

fsDir = FSDirectory.getDirectory(indexDir, False)
searcher = IndexSearcher(fsDir)

parser = QueryParser("keywords", StandardAnalyzer())
parser.setDefaultOperator(QueryParser.Operator.AND)
query = parser.parse(' '.join(args))
start = datetime.now()
hits = searcher.search(query)
duration = datetime.now() - start
if stats:
    print >> sys.stderr, "Found %d document(s) (in %s) that matched query '%s':" %(len(hits), duration, query)

for hit in hits:
    doc = Hit.cast_(hit).getDocument()
    table = dict((field.name(), field.stringValue())
                 for field in (Field.cast_(f) for f in doc.getFields()))
    print template.substitute(table)
