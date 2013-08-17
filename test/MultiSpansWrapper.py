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

import sys, lucene   # so that 'org' is found

from java.util import Collections, HashMap, TreeSet
from org.apache.lucene.index import Term, TermContext, ReaderUtil
from org.apache.lucene.search import DocIdSetIterator
from org.apache.lucene.search.spans import SpanQuery
from org.apache.pylucene.search.spans import PythonSpans


class MultiSpansWrapper(PythonSpans):

  def __init__(self, leaves, query, termContexts):
      super(MultiSpansWrapper, self).__init__()

      self.leaves = leaves
      self.numLeaves = leaves.size()
      self.query = query
      self.termContexts = termContexts
      self.leafOrd = 0
      self.current = None

  @classmethod
  def wrap(cls, topLevelReaderContext, query):

      termContexts = HashMap()
      terms = TreeSet()
      query.extractTerms(terms)
      for term in terms:
          termContexts.put(term, TermContext.build(topLevelReaderContext, term))

      leaves = topLevelReaderContext.leaves()
      if leaves.size() == 1:
          ctx = leaves.get(0)
          return query.getSpans(ctx, ctx.reader().getLiveDocs(), termContexts)

      return MultiSpansWrapper(leaves, query, termContexts)

  def next(self):

      if self.leafOrd >= self.numLeaves:
          return False

      if self.current is None:
          ctx = self.leaves.get(self.leafOrd)
          self.current = self.query.getSpans(ctx, ctx.reader().getLiveDocs(),
                                             self.termContexts)

      while True:
          if self.current.next():
              return True

          self.leafOrd += 1
          if self.leafOrd < self.numLeaves:
              ctx = self.leaves.get(self.leafOrd)
              self.current = self.query.getSpans(ctx, ctx.reader().getLiveDocs(), self.termContexts)
          else:
              self.current = None
              break

      return False

  def skipTo(self, target):

      if self.leafOrd >= self.numLeaves:
          return False

      subIndex = ReaderUtil.subIndex(target, self.leaves)
      assert subIndex >= self.leafOrd

      if subIndex != self.leafOrd:
          ctx = self.leaves.get(subIndex)
          self.current = self.query.getSpans(ctx, ctx.reader().getLiveDocs(),
                                             self.termContexts)
          self.leafOrd = subIndex
      elif self.current is None:
          ctx = self.leaves.get(self.leafOrd)
          self.current = self.query.getSpans(ctx, ctx.reader().getLiveDocs(),
                                             self.termContexts)

      while True:
          if self.current.skipTo(target - self.leaves.get(self.leafOrd).docBase):
              return True

          self.leafOrd += 1
          if self.leafOrd < self.numLeaves:
               ctx = self.leaves.get(self.leafOrd)
               self.current = self.query.getSpans(ctx, ctx.reader().getLiveDocs(), self.termContexts)
          else:
              self.current = None
              break

      return False

  def doc(self):
      if self.current is None:
          return DocIdSetIterator.NO_MORE_DOCS

      return self.current.doc() + self.leaves.get(self.leafOrd).docBase

  def start(self):
      if self.current is None:
          return DocIdSetIterator.NO_MORE_DOCS

      return self.current.start()

  def end(self):
      if self.current is None:
          return DocIdSetIterator.NO_MORE_DOCS

      return self.current.end()

  def getPayload(self):
      if self.current is None:
          return Collections.emptyList()

      return self.current.getPayload()

  def isPayloadAvailable(self):
      if self.current is None:
          return False

      return self.current.isPayloadAvailable()

  def cost(self):
      return sys.maxint
