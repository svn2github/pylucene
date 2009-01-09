# ====================================================================
# Copyright (c) 2004-2005 Open Source Applications Foundation.
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

from bsddb.db import DBEnv, DB
from bsddb.db import \
     DB_INIT_MPOOL, DB_INIT_LOCK, DB_INIT_TXN, DB_THREAD, DB_BTREE

# missing from python interface at the moment
DB_LOG_INMEMORY = 0x00020000

from lucene import DbDirectory, IndexSearcher, Term, TermQuery


class BerkeleyDbSearcher(object):

    def main(cls, argv):

        if len(argv) != 2:
            print "Usage: BerkeleyDbSearcher <index dir>"
            return

        dbHome = argv[1]

        env = DBEnv()
        env.set_flags(DB_LOG_INMEMORY, 1);
        if os.name == 'nt':
            env.set_cachesize(0, 0x4000000, 1)
        elif os.name == 'posix':
            from commands import getstatusoutput
            if getstatusoutput('uname') == (0, 'Linux'):
                env.set_cachesize(0, 0x4000000, 1)

        env.open(dbHome, (DB_THREAD |
                          DB_INIT_MPOOL | DB_INIT_LOCK | DB_INIT_TXN), 0)

        index = DB(env)
        blocks = DB(env)
        txn = None

        try:
            txn = env.txn_begin(None)
            index.open(filename = '__index__', dbtype = DB_BTREE,
                       flags = DB_THREAD, txn = txn)
            blocks.open(filename = '__blocks__', dbtype = DB_BTREE,
                        flags = DB_THREAD, txn = txn)
        except:
            if txn is not None:
                txn.abort()
                txn = None
            raise
        else:
            txn.commit()
            txn = None

        try:
            txn = env.txn_begin(None)
            directory = DbDirectory(txn, index, blocks, 0)
            searcher = IndexSearcher(directory)

            hits = searcher.search(TermQuery(Term("contents", "fox")))
            print len(hits), "document(s) found"
            searcher.close()
        except:
            if txn is not None:
                txn.abort()
                txn = None
            raise
        else:
            txn.abort()

            index.close()
            blocks.close()
            env.close()

    main = classmethod(main)
