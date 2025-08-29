For `SQueue` impl, makes it possible to "send" and object reference on a socket between two threads in same interpreter
```
>>> a = A()
>>> id(a)
4339315776
>>> import ctypes
>>> b = ctypes.cast(4339315776, ctypes.py_object).value
>>> b == a
True
>>> b is a
True
>>>
```
