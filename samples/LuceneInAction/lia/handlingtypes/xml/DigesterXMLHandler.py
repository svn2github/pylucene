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

import os

from lucene import Document, Field
from lia.handlingtypes.xml.Digester import Digester


class DigesterXMLHandler(object):

    def __init__(self):

        self.digester = digester = Digester()

        digester.addSetProperty("address-book/contact", "type", "type")
        digester.addSetProperty("address-book/contact/name", "name")
        digester.addSetProperty("address-book/contact/address", "address")
        digester.addSetProperty("address-book/contact/city", "city")
        digester.addSetProperty("address-book/contact/province", "province")
        digester.addSetProperty("address-book/contact/postalcode", "postalcode")
        digester.addSetProperty("address-book/contact/country", "country")
        digester.addSetProperty("address-book/contact/telephone", "telephone")

    def indexFile(self, writer, path):

        try:
            file = open(path)
        except IOError, e:
            raise
        else:
            props = self.digester.parse(file)
            doc = Document()
            doc.add(Field("type", props['type'],
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            doc.add(Field("name", props['name'],
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            doc.add(Field("address", props['address'],
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            doc.add(Field("city", props['city'],
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            doc.add(Field("province", props['province'],
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            doc.add(Field("postalcode", props['postalcode'],
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            doc.add(Field("country", props['country'],
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            doc.add(Field("telephone", props['telephone'],
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            doc.add(Field("filename", os.path.abspath(path),
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            writer.addDocument(doc)
            file.close()

            return doc
