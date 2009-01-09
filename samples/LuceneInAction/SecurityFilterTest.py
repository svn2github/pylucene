
import os, sys, unittest, lucene
lucene.initVM(lucene.CLASSPATH)

sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))

import lia.advsearching.SecurityFilterTest
unittest.main(lia.advsearching.SecurityFilterTest)
