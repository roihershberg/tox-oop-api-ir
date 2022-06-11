# IRFunction

```json
{
  "object_name": "IRFunction",
  "name": string,
  "cname": string,
  "return_type": "[IRType](../type)",
  "replaced_return_type": "[IRType](../type)",
  "throws": string,
  "is_static": boolean,
  "params": "[[IRParam](../param) | [IRBufferWrapper](../buffer_wrapper), ...]"
}
```

`name`

:   The name of the function.

    E.g. `#!json bootstrap`.

`cname`

:   The original name of the function.

    E.g. `#!json tox_bootstrap`.

`return_type`

:   The return type of the function.

    See [IRType](../type).

`replaced_return_type` (<span class="nullable">Nullable</span>)

:   If not `#!json null`, this signifies that the original return type (described in this field) was
    replaced with a different one (the one in `return_type`) as part of an optimization.

    The current optimizations that would result in the replacement of the types are:

     - Converting of buffer getters. Instead of passing a pointer to the buffer as a parameter
       to the function, the buffer will be the returned object.

     - Removal of boolean returned when the function throws an exception. If a function throws
       an exception and it returns a `bool` indicating whether an error has occured, the `bool`
       will be converted to `void` as the catching of the exception is now the indication of
       an error.

    This is useful for example when the value in this field is a `bool` type. In this case
    the binding should check if the returned `bool` from the C function was `#!c false` and
    if it was, then throw an exception, either from the `throws` field or a general one if
    `#!json null`.

    See [IRType](../type).

`throws` (<span class="nullable">Nullable</span>)

:   The name of the exception to throw.

    The [IRException](../exception) object should be retrieved from the `exceptions` list in
    the root of the JSON by the `name` field. This indicates that the function has an additional
    parameter in the end expecting a pointer to the enum described in the `enum_name` field in the
    [IRException](../exception) object. The function should check if the error is not `OK`
    or if the returned value is a `bool` then that it's `#!c false` (see `replaced_return_type`
    above). If it is, then the function should throw the exception.

    E.g. `#!json "ToxOptionsNew"`.

`is_static`

:   If `#!json true` then the parameters to the C function should be passed as usual from the
    binding function. If `#!json false` then the parameters to the C function should first be
    the handles of the current class hierarchy and then any other parameters.

    See the `inner_classes` field in [IRClass](../class) to see more information and an example.

`params`

:   The list of the parameters of the function. These can be represented by either [IRParam](../param)
    or [IRBufferWrapper](../buffer_wrapper).
