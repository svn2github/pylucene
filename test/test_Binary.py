# ====================================================================
#   Copyright (c) 2004-2008 Open Source Applications Foundation
#
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

# test PyLucene binary field

from unittest import TestCase, main
from lucene import Field

class BinaryTestCase(TestCase):

    def binary(self, b):

        c = ''.join([chr(a) for a in b])
        field = Field("bin", c, Field.Store.YES)
        v = field.binaryValue()
        assert c == v and b == [ord(a) for a in v]

    def testBinary(self):

        self.binary([66, 90, 104, 57, 49, 65, 89, 38,
                     83, 89, 105, 56, 95, 75, 0, 0, 14, 215, 128])
        self.binary([])
        self.binary([0, 0, 0])


if __name__ == '__main__':
    import sys, lucene
    lucene.initVM(lucene.CLASSPATH)
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                main()
            except:
                pass
    else:
        main()
