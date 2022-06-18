# IRFunction

```json
{
  "object_name": "IRFunction",
  "name": string,
  "cname": string,
  "return_type": "[IRReturnType](../return_type)",
  "throws": string,
  "is_static": boolean,
  "params": "[[IRParam](../param) | [IRBufferWrapper](../buffer_wrapper), ...]"
}
```

`name`

:   The name of the function.

    E.g. `#!json "bootstrap"`.

`cname`

:   The original name of the function.

    E.g. `#!json "tox_bootstrap"`.

`return_type`

:   The return type spec of the function.

    See [IRReturnType](../return_type).

`throws` (<span class="nullable">Nullable</span>)

:   The name of the exception to throw.

    The [IRException](../exception) object should be retrieved from the `exceptions` list in
    the root of the JSON by the `name` field. This indicates that the function has an additional
    parameter in the end expecting a pointer to the enum described in the `enum_name` field in the
    [IRException](../exception) object. The function should check if the error is not `OK`
    or if the returned value is a `bool` then that it's `#!c false` (see `replaced` in `return_type`
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
