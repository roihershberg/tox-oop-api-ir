# IRReturnType

```json
{
  "object_name": "IRReturnType",
  "type": "[IRType](../type)",
  "replaced": "[IRType](../type)",
  "param_index": int
}
```

`type`

:   The current return type.

    See [IRType](../type).

`replaced` (<span class="nullable">Nullable</span>)

:   If not `#!json null`, this signifies that the original return type (described in this field) was
    replaced with a different one (the one in `type`) as part of an optimization.

    The current optimizations that would result in the replacement of the types are:

     - Converting of buffer getters. Instead of passing a pointer to the buffer as a parameter
       to the function, the buffer will be the returned object.

     - Removal of boolean returned when the function throws an exception. If a function throws
       an exception and it returns a `bool` indicating whether an error has occured, the `bool`
       will be converted to `void` as the catching of the exception is now the indication of
       an error.

    This is useful for example when the value in this field is a `bool` type. In this case
    the binding should check if the returned `bool` from the C function was `#!c false` and
    if it was, then throw an exception, either from the `throws` field in [IRFunction](../function)
    or a general one if `#!json null`.

    See [IRType](../type).

`param_index` (<span class="nullable">Nullable</span>)

:   If not `#!json null`, this is used for passing the `type` to the C function in the correct parameter
    position as part of an optimization of buffer getter (see `replaced` above).

    E.g. `#!json 0`
