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

import sys, lucene, unittest
from lucene.collections import JavaSet, JavaList

from java.lang import Class, Boolean, Integer, Long, Double, String
from java.util import ArrayList, HashSet


class Test_CollectionsSetBase(unittest.TestCase):
    """base test case for JavaSet (uses integers)
       subclass may redefine method 'createTestSet'
    """

    def createTestSet(self):
        """creates the test set for this test case
        """
        return set(range(9))

    def setUp(self):
        self.testSet = self.createTestSet()
        self.javaSet = JavaSet(self.testSet)
        # print "created testSet: %s JavaSet %s" % (self.testSet,self.javaSet)

    def tearDown(self):
        del self.testSet
        del self.javaSet

    def test_Contains(self):
        elem0 = list(self.testSet)[0]
        self.assertTrue(self.javaSet.contains(elem0))

    def test_Size(self):
        self.assertEqual(len(self.testSet), self.javaSet.size())

    def test_Add(self):
        """must fail to add an existing element
        """
        elem0 = list(self.testSet)[0]
        self.assertFalse(self.javaSet.add(elem0))
        self.assertEqual(len(self.testSet),
                         self.javaSet.size(),
                         "size has not changed")

    def test_HashSet(self):
        """create HashSet in JVM (from the JavaSet)
        """
        hashSet = HashSet(self.javaSet)
        # print "created HashSet:", hashSet, type(hashSet)
        self.assertEqual(self.javaSet.size(),
                         hashSet.size(),
                         "HashSet has same size")
        elem0 = list(self.testSet)[0]
        self.assertTrue(hashSet.contains(elem0))

    def test_JArray(self):
        """create JArray in JVM (from the JavaSet)
        """
        jArray = self.javaSet.toArray()
        # print "created JArray:", jArray, type(jArray)
        self.assertEqual(self.javaSet.size(),len(jArray),
                         "JArray has same size")
        elem0 = jArray[0]
        elem1 = jArray[1]
        # print "JArray: first element: %s (%s)" % (elem0,type(elem0))
        # print "JArray: second element: %s (%s)"% (elem1,type(elem1))

    def test_ArrayList(self):
        """create ArrayList in JVM (from the JavaSet)
        """
        arrayList = ArrayList(self.javaSet)
        # print "created ArrayList:", arrayList, type(arrayList)
        self.assertEqual(self.javaSet.size(), arrayList.size(),
                         "ArrayList has same size")
        elem0 = arrayList.get(0)
        elem1 = arrayList.get(1)
        # print "ArrayList: first element: %s (%s) indexOf=%d" % (elem0,type(elem0), arrayList.indexOf(elem0))
        # print "ArrayList: second element: %s (%s) indexOf=%d" % (elem1,type(elem1), arrayList.indexOf(elem1))
        self.assertFalse(elem0.equals(elem1),
                         "ArrayList: first element must NOT equal second element")
        self.assertNotEqual(elem0, elem1,
                            "ArrayList: first element must NOT equal second element")


class Test_CollectionsStringSet(Test_CollectionsSetBase):

    def createTestSet(self):
        return set(['a','b','c'])


class Test_CollectionsFloatSet(Test_CollectionsSetBase):

    def createTestSet(self):
        return set([1.5, 4.5, -0.5])


class Test_CollectionsBoolSet(Test_CollectionsSetBase):

    def createTestSet(self):
        return set([True,False])


class Test_CollectionsListBase(unittest.TestCase):
    """base test case for JavaList (uses integers)
       subclass may redefine method 'createTestList'
    """

    def __init__(self, *args, **kwds):
        unittest.TestCase.__init__(self, *args, **kwds)

        self._primitive_types = {
            Class.forName('java.lang.Boolean'): Boolean,
            Class.forName('java.lang.Integer'): Integer,
            Class.forName('java.lang.Long'): Long,
            Class.forName('java.lang.Double'): Double,
            Class.forName('java.lang.String'): String
        }

    def createTestList(self):
        """creates the test list for this test case
        """
        return range(9)

    def setUp(self):
        self.testList = self.createTestList()
        self.javaList = JavaList(self.testList)
        # print "created testList: %s JavaList %s" % (self.testList,self.javaList)

    def tearDown(self):
        del self.testList
        del self.javaList

    def test_Contains(self):
        elem0 = self.testList[0]
        self.assertTrue(self.javaList.contains(elem0))

    def test_Size(self):
        self.assertEqual(len(self.testList), self.javaList.size())

    def test_Pos(self):
        """elements must have same position
        """
        elem0 = self.testList[0]
        elem1 = self.testList[1]
        pos0 = self.javaList.indexOf(elem0)
        pos1 = self.javaList.indexOf(elem1)
        self.assertEqual(pos0, 0, "indexOf first element")
        self.assertEqual(pos1, 1, "indexOf second element")

    def test_HashSet(self):
        """create HashSet in JVM (from the JavaSet)
        """
        hashSet = HashSet(self.javaList)
        # print "created HashSet:", hashSet, type(hashSet)
        self.assertEqual(self.javaList.size(),
                         hashSet.size(),
                         "HashSet has same size")
        elem0 = self.testList[0]
        self.assertTrue(hashSet.contains(elem0))

    def test_JArray(self):
        """create JArray in JVM (from the JavaSet)
        """
        jArray = self.javaList.toArray()
        # print "created JArray:", jArray, type(jArray)
        self.assertEqual(self.javaList.size(),len(jArray),
                         "JArray has same size")
        elem0 = jArray[0]
        elem1 = jArray[1]
        listElem0 = self.testList[0]
        listElem1 = self.testList[1]

        self.assertEqual(elem0, listElem0,
                         "should be equal: %s (%s) <-> %s (%s)" % (
                            elem0,type(elem0), listElem0, type(listElem0)))

        self.assertEqual(elem1, listElem1,
                         "should be equal: %s (%s) <-> %s (%s)" % (
                            elem1,type(elem1), listElem1, type(listElem1)))

        self.assertEqual(type(elem0), type(listElem0),
                         "should have same type: %s <-> %s" % (
                            type(elem0), type(listElem0)))

        self.assertNotEqual(elem0, elem1,
                            "JArray: first element must NOT equal second element")

    def test_ArrayList(self):
        """create ArrayList in JVM (from the JavaSet)
        """
        arrayList = ArrayList(self.javaList)
        # print "created ArrayList:", arrayList, type(arrayList)
        self.assertEqual(self.javaList.size(), arrayList.size(),
                         "ArrayList has same size")
        elem0 = arrayList.get(0)
        elem1 = arrayList.get(1)
        self.assertEqual(0, arrayList.indexOf(elem0), "same index position")
        self.assertEqual(1, arrayList.indexOf(elem1), "same index position")
        listElem0 = self.testList[0]
        listElem1 = self.testList[1]

        _type = self._primitive_types.get(elem0.getClass())
        if _type is not None:
            elem0 = _type.class_.cast(elem0)
            elem1 = _type.class_.cast(elem1)

        self.assertEqual(elem0, listElem0,
                         "should be equal: %s (%s) <-> %s (%s)" % (
                            elem0, type(elem0), listElem0, type(listElem0)))

        self.assertEqual(elem1, listElem1,
                         "should be equal: %s (%s) <-> %s (%s)" % (
                            elem1, type(elem1), listElem1, type(listElem1)))

        self.assertEqual(type(elem0), type(listElem0),
                         "should have same type: %s <-> %s" % (
                            type(elem0), type(listElem0)))

        self.assertNotEqual(elem0, elem1,
                            "ArrayList: first element must NOT equal second element")



class Test_CollectionsStringList(Test_CollectionsListBase):

    def createTestList(self):
        return [u'a', u'b', u'c']


class Test_CollectionsFloatList(Test_CollectionsListBase):

    def createTestList(self):
        return [1.5, 4.5, -0.5]


class Test_CollectionsBoolList(Test_CollectionsListBase):

    def createTestList(self):
        return [True,False]


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    unittest.main()
