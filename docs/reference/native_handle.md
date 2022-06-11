# IRNativeHandle

```json
{
  "object_name": "IRNativeHandle",
  "alloc_func": "[IRFunction](../function)",
  "dealloc_func": "[IRFunction](../function)"
}
```

`alloc_func` (<span class="nullable">Nullable</span>)

:   If not `#!json null`, this function represents a C function that should be called to get
    a newly allocated handle.
    
    If `#!json null`, then the object (and the handle) can be constructed only from
    other functions (and not the constructor).
    
    See [IRFunction](../function).

`dealloc_func`

:   This function represents a C function that should be called to release the memory of the resource(s)
    the handle is associated with. Must be called when the class object is released (or garbage collected)
    or earlier at the client's choice.

    See [IRFunction](../function).
