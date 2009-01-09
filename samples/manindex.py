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
# to index all man pages on $MANPATH or /usr/share/man:
#   python manindex.py pages
# ====================================================================

import os, re, sys
from subprocess import *
from lucene import IndexWriter, StandardAnalyzer, Document, Field
from lucene import initVM, CLASSPATH

def indexDirectory(dir):

    for name in os.listdir(dir):
        path = os.path.join(dir, name)
        if os.path.isfile(path):
            indexFile(dir, name)


def indexFile(dir,filename):

    path = os.path.join(dir, filename)
    print "  File: ", filename

    if filename.endswith('.gz'):
        child = Popen('gunzip -c ' + path + ' | groff -t -e -E -mandoc -Tascii | col -bx', shell=True, stdout=PIPE, cwd=os.path.dirname(dir)).stdout
        command, section = re.search('^(.*)\.(.*)\.gz$', filename).groups()
    else:
        child = Popen('groff -t -e -E -mandoc -Tascii ' + path + ' | col -bx',
                      shell=True, stdout=PIPE, cwd=os.path.dirname(dir)).stdout
        command, section = re.search('^(.*)\.(.*)$', filename).groups()

    data = child.read()
    err = child.close()
    if err:
        raise RuntimeError, '%s failed with exit code %d' %(command, err)

    matches = re.search('^NAME$(.*?)^\S', data,
                        re.MULTILINE | re.DOTALL)
    name = matches and matches.group(1) or ''

    matches = re.search('^(?:SYNOPSIS|SYNOPSYS)$(.*?)^\S', data,
                        re.MULTILINE | re.DOTALL)
    synopsis = matches and matches.group(1) or ''

    matches = re.search('^(?:DESCRIPTION|OVERVIEW)$(.*?)', data,
                        re.MULTILINE | re.DOTALL)
    description = matches and matches.group(1) or ''

    doc = Document()
    doc.add(Field("command", command,
                  Field.Store.YES, Field.Index.UN_TOKENIZED))
    doc.add(Field("section", section,
                  Field.Store.YES, Field.Index.UN_TOKENIZED))
    doc.add(Field("name", name.strip(),
                  Field.Store.YES, Field.Index.TOKENIZED))
    doc.add(Field("synopsis", synopsis.strip(),
                  Field.Store.YES, Field.Index.TOKENIZED))
    doc.add(Field("keywords", ' '.join((command, name, synopsis, description)),
                  Field.Store.NO, Field.Index.TOKENIZED))
    doc.add(Field("filename", os.path.abspath(path),
                  Field.Store.YES, Field.Index.UN_TOKENIZED))

    writer.addDocument(doc)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "Usage: python manindex.py <index dir>"

    else:
        initVM(CLASSPATH)
        indexDir = sys.argv[1]
        writer = IndexWriter(indexDir, StandardAnalyzer(), True)
        manpath = os.environ.get('MANPATH', '/usr/share/man').split(os.pathsep)
        for dir in manpath:
            print "Crawling", dir
            for name in os.listdir(dir):
                path = os.path.join(dir, name)
                if os.path.isdir(path):
                    indexDirectory(path)
        writer.optimize()
        writer.close()
