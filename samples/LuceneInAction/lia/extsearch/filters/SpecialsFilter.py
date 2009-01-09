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

from lucene import IndexReader, Term, BitSet, PythonFilter, JArray

#
# A Filter extension, with a TermDocs wrapper working around the lack of
# support for returning values in array arguments.
#
class SpecialsFilter(PythonFilter):

    def __init__(self, accessor):
        
        super(SpecialsFilter, self).__init__()
        self.accessor = accessor

    def bits(self, reader):

        bits = BitSet(reader.maxDoc())
        isbns = self.accessor.isbns()

        for isbn in isbns:
            if isbn is not None:
                termDocs = reader.termDocs(Term("isbn", isbn))
                docs = JArray(int)(1)
                freq = JArray(int)(1)
                if termDocs.read(docs, freq) == 1:
                    bits.set(docs[0])

        return bits

    def __str__():

        return "SpecialsFilter"
