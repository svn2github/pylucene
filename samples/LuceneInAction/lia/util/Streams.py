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

from StringIO import StringIO
from HTMLParser import HTMLParser


class InputStreamReader(object):

    def __init__(self, inputStream, encoding):

        super(InputStreamReader, self).__init__()
        self.inputStream = inputStream
        self.encoding = encoding or 'utf-8'

    def _read(self, length):

        return self.inputStream.read(length)

    def read(self, length=-1):

        text = self._read(length)
        text = unicode(text, self.encoding)

        return text

    def close(self):

        self.inputStream.close()


class HTMLReader(object):

    def __init__(self, reader):

        self.reader = reader

        class htmlParser(HTMLParser):

            def __init__(self):

                HTMLParser.__init__(self)

                self.buffer = StringIO()
                self.position = 0

            def handle_data(self, data):

                self.buffer.write(data)

            def _read(self, length):

                buffer = self.buffer
                size = buffer.tell() - self.position

                if length > 0 and size > length:
                    buffer.seek(self.position)
                    data = buffer.read(length)
                    self.position += len(data)
                    buffer.seek(0, 2)

                elif size > 0:
                    buffer.seek(self.position)
                    data = buffer.read(size)
                    self.position = 0
                    buffer.seek(0)

                else:
                    data = ''

                return data
                
        self.parser = htmlParser()

    def read(self, length=-1):

        while True:
            data = self.reader.read(length)
            if len(data) > 0:
                self.parser.feed(data)
                data = self.parser._read(length)
                if len(data) == 0:
                    continue
            return data

    def close(self):

        self.reader.close()
