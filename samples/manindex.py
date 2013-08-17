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
# Author: Erik Hatcher
#
# to index all man pages on $MANPATH or /usr/share/man:
#   python manindex.py pages
# ====================================================================

import os, re, sys, lucene
from subprocess import *

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

def indexDirectory(dir):

    for name in os.listdir(dir):
        path = os.path.join(dir, name)
        if os.path.isfile(path):
            indexFile(dir, name)


def indexFile(dir, filename):

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
    doc.add(Field("command", command, StringField.TYPE_STORED))
    doc.add(Field("section", section, StringField.TYPE_STORED))
    doc.add(Field("name", name.strip(), TextField.TYPE_STORED))
    doc.add(Field("synopsis", synopsis.strip(), TextField.TYPE_STORED))
    doc.add(Field("keywords", ' '.join((command, name, synopsis, description)),
                  TextField.TYPE_NOT_STORED))
    doc.add(Field("filename", os.path.abspath(path), StringField.TYPE_STORED))

    writer.addDocument(doc)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "Usage: python manindex.py <index dir>"

    else:
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        directory = SimpleFSDirectory(File(sys.argv[1]))
        analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
        analyzer = LimitTokenCountAnalyzer(analyzer, 10000)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        writer = IndexWriter(directory, config)

        manpath = os.environ.get('MANPATH', '/usr/share/man').split(os.pathsep)
        for dir in manpath:
            print "Crawling", dir
            for name in os.listdir(dir):
                path = os.path.join(dir, name)
                if os.path.isdir(path):
                    indexDirectory(path)
        writer.commit()
        writer.close()
