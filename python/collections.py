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

import sys
from lucene import JArray

from java.lang import IllegalStateException, IndexOutOfBoundsException
from java.util import NoSuchElementException
from org.apache.pylucene.util import \
    PythonSet, PythonList, PythonIterator, PythonListIterator


if sys.version_info[0] > 2:
    def next(iterator):
        return iterator.__next__();
else:
    def next(iterator):
        return iterator.next()


class JavaSet(PythonSet):
    """
    This class implements java.util.Set around a Python set instance it wraps.
    """

    def __init__(self, _set):
        super(JavaSet, self).__init__()
        self._set = _set

    def __contains__(self, obj):
        return obj in self._set

    def __len__(self):
        return len(self._set)

    def __iter__(self):
        return iter(self._set)

    def add(self, obj):
        if obj not in self._set:
            self._set.add(obj)
            return True
        return False

    def addAll(self, collection):
        size = len(self._set)
        self._set.update(collection)
        return len(self._set) > size

    def clear(self):
        self._set.clear()

    def contains(self, obj):
        return obj in self._set

    def containsAll(self, collection):
        for obj in collection:
            if obj not in self._set:
                return False
        return True

    def equals(self, collection):
        if type(self) is type(collection):
            return self._set == collection._set
        return False

    def isEmpty(self):
        return len(self._set) == 0

    def iterator(self):
        class _iterator(PythonIterator):
            def __init__(_self):
                super(_iterator, _self).__init__()
                _self._iterator = iter(self._set)
            def hasNext(_self):
                if hasattr(_self, '_next'):
                    return True
                try:
                    _self._next = next(_self._iterator)
                    return True
                except StopIteration:
                    return False
            def next(_self):
                if hasattr(_self, '_next'):
                    next = _self._next
                    del _self._next
                else:
                    next = next(_self._iterator)
                return next
        return _iterator()

    def remove(self, obj):
        try:
            self._set.remove(obj)
            return True
        except KeyError:
            return False

    def removeAll(self, collection):
        result = False
        for obj in collection:
            try:
                self._set.remove(obj)
                result = True
            except KeyError:
                pass
        return result

    def retainAll(self, collection):
        result = False
        for obj in list(self._set):
            if obj not in collection:
                self._set.remove(obj)
                result = True
        return result

    def size(self):
        return len(self._set)

    def toArray(self):  # JavaSet
        return list(self._set)


class JavaListIterator(PythonListIterator):
    """
    This class implements java.util.ListIterator for a Python list instance it
    wraps. (simple bidirectional iterator)
    """
    def __init__(self, _lst, index=0):
        super(JavaListIterator, self).__init__()
        self._lst = _lst
        self._lastIndex = -1 # keep state for remove/set
        self.index = index

    def next(self):
        if self.index >= len(self._lst):
            raise JavaError(NoSuchElementException(str(self.index)))
        result = self._lst[self.index]
        self._lastIndex = self.index
        self.index += 1
        return result

    def previous(self):
        if self.index <= 0:
            raise JavaError(NoSuchElementException(str(self.index - 1)))
        self.index -= 1
        self._lastIndex = self.index
        return self._lst[self.index]

    def hasPrevious(self):
        return self.index > 0

    def hasNext(self):
        return self.index < len(self._lst)

    def nextIndex(self):
        return min(self.index, len(self._lst))

    def previousIndex(self):
        return max(-1, self.index - 1)

    def add(self, element):
        """
        Inserts the specified element into the list.
        The element is inserted immediately before the next element
        that would be returned by next, if any, and after the next
        element that would be returned by previous, if any.
        """
        if self._lastIndex < 0:
            raise JavaError(IllegalStateException("add"))
        self._lst.insert(self.index, element)
        self.index += 1
        self._lastIndex = -1 # invalidate state

    def remove(self):
        """
        Removes from the list the last element that
        was returned by next or previous.
        """
        if self._lastIndex < 0:
            raise JavaError(IllegalStateException("remove"))
        del self._lst[self._lastIndex]
        self._lastIndex = -1 # invalidate state

    def set(self, element):
        """
        Replaces the last element returned by next or previous
        with the specified element.
        """
        if self._lastIndex < 0:
            raise JavaError(IllegalStateException("set"))
        self._lst[self._lastIndex] = element

    def __iter__(self):
        return self


class JavaList(PythonList):
    """
    This class implements java.util.List around a Python list instance it wraps.
    """

    def __init__(self, _lst):
        super(JavaList, self).__init__()
        self._lst = _lst

    def __contains__(self, obj):
        return obj in self._lst

    def __len__(self):
        return len(self._lst)

    def __iter__(self):
        return iter(self._lst)

    def add(self, index, obj):
        self._lst.insert(index, obj)

    def addAll(self, collection):
        size = len(self._lst)
        self._lst.extend(collection)
        return len(self._lst) > size

    def addAll(self, index, collection):
        size = len(self._lst)
        self._lst[index:index] = collection
        return len(self._lst) > size

    def clear(self):
        del self._lst[:]

    def contains(self, obj):
        return obj in self._lst

    def containsAll(self, collection):
        for obj in collection:
            if obj not in self._lst:
                return False
        return True

    def equals(self, collection):
        if type(self) is type(collection):
            return self._lst == collection._lst
        return False

    def get(self, index):
        if index < 0 or index >= self.size():
            raise JavaError(IndexOutOfBoundsException(str(index)))
        return self._lst[index]

    def indexOf(self, obj):
        try:
            return self._lst.index(obj)
        except ValueError:
            return -1

    def isEmpty(self):
        return len(self._lst) == 0

    def iterator(self):
        class _iterator(PythonIterator):
            def __init__(_self):
                super(_iterator, _self).__init__()
                _self._iterator = iter(self._lst)
            def hasNext(_self):
                if hasattr(_self, '_next'):
                    return True
                try:
                    _self._next = next(_self._iterator)
                    return True
                except StopIteration:
                    return False
            def next(_self):
                if hasattr(_self, '_next'):
                    next = _self._next
                    del _self._next
                else:
                    next = next(_self._iterator)
                return next
        return _iterator()

    def lastIndexOf(self, obj):
        i = len(self._lst)-1
        while (i>=0):
            if obj.equals(self._lst[i]):
                break
            i -= 1
        return i

    def listIterator(self, index=0):
        return JavaListIterator(self._lst, index)

    def remove(self, obj_or_index):
        if type(obj_or_index) is type(1):
            return removeAt(int(obj_or_index))
        return removeElement(obj_or_index)

    def removeAt(self, pos):
        """
        Removes the element at the specified position in this list.
        Note: private method called from Java via remove(int index)
        index is already checked (or IndexOutOfBoundsException thrown)
        """
        try:
            el = self._lst[pos]
            del self._lst[pos]
            return el
        except IndexError:
            # should not happen
            return None

    def removeObject(self, obj):
        """
        Removes the first occurrence of the specified object
        from this list, if it is present
        """
        try:
            self._lst.remove(obj)
            return True
        except ValueError:
            return False

    def removeAll(self, collection):
        result = False
        for obj in collection:
            if self.removeElement(obj):
                result = True
        return result

    def retainAll(self, collection):
        result = False
        for obj in self._lst:
            if obj not in collection and self.removeElement(obj):
                result = True
        return result

    def size(self):
        return len(self._lst)

    def toArray(self):
        return self._lst

    def subListChecked(self, fromIndex, toIndex):
        """
        Note: private method called from Java via subList()
        from/to index are already checked (or IndexOutOfBoundsException thrown)
        also IllegalArgumentException is thronw if the endpoint indices
        are out of order (fromIndex > toIndex)
        """
        sublst = self._lst[fromIndex:toIndex]
        return JavaList(sublst)

    def set(self, index, obj):
        if index < 0 or index >= self.size():
            raise JavaError(IndexOutOfBoundsException(str(index)))
        self._lst[index] = obj
