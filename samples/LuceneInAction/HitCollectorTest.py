
import os, sys, unittest, lucene
lucene.initVM(lucene.CLASSPATH)

baseDir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(baseDir)

import lia.extsearch.hitcollector.HitCollectorTest
from lucene import System

System.setProperty("index.dir", os.path.join(baseDir, 'index'))
unittest.main(lia.extsearch.hitcollector.HitCollectorTest)
