
from lucene import PythonSet, PythonIterator, JavaError


class JavaSet(PythonSet):

    def __init__(self, _set):
        super(JavaSet, self).__init__()
        self._set = _set

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
                    _self._next = _self._iterator.next()
                    return True
                except StopIteration:
                    return False
            def next(_self):
                if hasattr(_self, '_next'):
                    next = _self._next
                    del _self._next
                else:
                    next = _self._iterator.next()
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
            if obj not in c:
                self._set.remove(obj)
                result = True
        return result

    def size(self):
        return len(self._set)

    def toArray(self):
        return list(self._set)

