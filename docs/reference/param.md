# IRParam

```json
{
  "object_name": "IRParam",
  "name": string,
  "type": "[IRType](../type)",
  "replaced_type": "[IRType](../type)"
}
```

This object represents a parameter in a function.

`name`

:   The name of the parameter.

`type`

:   The type of the parameter.
    
    See [IRType](../type).

`replaced_type` (<span class="nullable">Nullable</span>)

:   If not `#!json null` this will be the original type of the parameter. Currently, this is used in `dealloc_func`
    in [IRNativeHandle](../native_handle) where the pointer parameter is replaced with a `ulong` (described in `type`)
    as this is the type that should be used to store the native handle (the pointer). The binding should then convert
    the `ulong` to the type described in this field (pointer to some struct).
    
    See [IRType](../type).
