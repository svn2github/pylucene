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

import xml.sax


class Digester(xml.sax.ContentHandler):

    attributes = {}
    tags = {}

    def addSetProperty(self, path, property, attribute=None):

        if attribute is not None:
            pairs = self.attributes.get(path)
            if pairs is None:
                self.attributes[path] = pairs = { attribute: property }
            else:
                pairs[property] = attribute

        else:
            self.tags[path] = property

    def parse(self, input):

        xml.sax.parse(input, self)
        return self.properties
    
    def startDocument(self):

        self.properties = {}
        self.path = []

    def startElement(self, tag, attrs):

        self.path.append(tag)
        pairs = self.attributes.get('/'.join(self.path))
        if pairs is not None:
            for name, value in attrs.items():
                property = pairs.get(name)
                if property is not None:
                    self.properties[property] = value

    def characters(self, data):

        self.data = data.strip()

    def endElement(self, tag):

        if self.data:
            property = self.tags.get('/'.join(self.path))
            if property is not None:
                self.properties[property] = self.data
            self.data = None
            
        self.path.pop()
