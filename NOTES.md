For `SQueue` impl
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
