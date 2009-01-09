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

import os, popen2

from lucene import Document, Field, StringReader
from lia.util.Streams import InputStreamReader


class AntiWordHandler(object):

    def indexFile(self, writer, path):

        doc = Document()

        try:
            process = popen2.Popen4(["antiword", "-m", "UTF-8", path])
            string = InputStreamReader(process.fromchild, 'utf-8').read()
        except:
            raise
        else:
            doc.add(Field("contents", StringReader(string)))
            doc.add(Field("filename", os.path.abspath(path),
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            writer.addDocument(doc)

            exitCode = process.wait()
            if exitCode != 0:
                raise RuntimeError, "pdftotext exit code %d" %(exitCode)

            return doc
