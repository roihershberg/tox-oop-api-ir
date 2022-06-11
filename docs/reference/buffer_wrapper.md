# IRBufferWrapper

```json
{
  "object_name": "IRBufferWrapper",
  "buffer_param": "[IRParam](../param)",
  "length_param": "[IRParam](../param)"
}
```

This object wraps two parameters into one - a buffer and its length.
This means that the API should require only one parameter - a certain
array whose type is determined from the `type` field in the `buffer_param`
object and under the hood the binding will extract the array into a pointer
and a length and pass them to the C function.

`buffer_param`

:   The original parameter of the buffer.
    
    See [IRParam](../param).

`length_param`

:   The original parameter of the length of the buffer.

    See [IRParam](../param).

## Important notes

The type and the name of the parameter to include in the API function should
be the `type` and the `name` in the `buffer_param`.
