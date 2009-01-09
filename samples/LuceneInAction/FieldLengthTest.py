
import os, sys, unittest, lucene
lucene.initVM(lucene.CLASSPATH)

sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))

import lia.indexing.FieldLengthTest
unittest.main(lia.indexing.FieldLengthTest)
