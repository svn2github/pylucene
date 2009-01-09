
import os, sys, lucene
lucene.initVM(lucene.CLASSPATH)

sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))

from lia.analysis.AnalyzerDemo import AnalyzerDemo
AnalyzerDemo.main(sys.argv)
