# ====================================================================
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

# This sample illustrates how to use a thread with PyLucene

INDEX_DIR = "ThreadIndexFiles.index"

import sys, os, threading, lucene

from datetime import datetime
from IndexFiles import IndexFiles

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.util import Version


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    env=lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION

    def fn():
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        env.attachCurrentThread()
        start = datetime.now()
        IndexFiles(sys.argv[1], os.path.join(base_dir, INDEX_DIR),
                   StandardAnalyzer(Version.LUCENE_CURRENT))
        end = datetime.now()
        print end - start

    threading.Thread(target=fn).start()
