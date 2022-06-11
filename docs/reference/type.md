# IRType

```json
{
  "object_name": "IRType",
  "name": string,
  "mutable": boolean,
  "is_array": boolean,
  "acts_as_string": boolean,
  "contains_number_handle": boolean,
  "ctype": "[CType](../ctype)",
  "get_size_func": "[IRFunction](../function)",
  "set_size_func": "[IRFunction](../function)"
}
```

`name`

:   The name of the type modified and mapped from the C type.
    The current mapping is as follows (the original C type in
    the left and the one stored in this field to the right):

    `uint8_t` -> `byte`<br>
    `uint16_t` -> `ushort`<br>
    `uint32_t` -> `uint`<br>
    `uint64_t` -> `ulong`<br>
    `size_t` -> `ulong`<br>
    `char` -> `char`<br>
    `bool` -> `bool`<br>
    `void` -> `void`<br>

    If the type doesn't have a corresponding mapping the underscores
    in the name are removed (if any) and the first letter of each word
    is uppercased forming a PascalCase.

`mutable`

:   If the value of the variable can be changed after assignment.
    Either `#!json true` or `#!json false`.

`is_array`

:   If the type is an array. If the type is primitive
    (has been mapped using the above mapping) and the `is_pointer` field
    of the `ctype` object is `#!json true` this will be `#!json true`, otherwise `#!json false`.

`acts_as_string`

:   This will be `#!json true` if the type is a part of an [IRParam](../param) and it meets the
    following requirements:

     - The `name` of the containing [IRParam](../param) contains one of the following strings:
        `#!json ["name", "title", "message"]`.
     - The `name` of the `ctype` object equals to `uint8_t`.
     - The `is_array` field is `#!json true`.

    This signifies that the front-facing API should treat this type as a string and perform
    the neccessary casts to an array of bytes (`uint8_t`) and vice versa.

`contains_number_handle`

:   If this is `#!json true`, this represents that the original type was a number handle and
    has been replaced by a wrapper class - specified in the `name` field. If this is a parameter
    to a function, the API should get an instance of the wrapper class instead of a number and under
    the hood pass the number handle stored in the class to the C function. If it's a return type, then
    the binding should get the number handle returned by the C function, wrap it in a new instance of
    the wrapper class and return it instead.

`ctype`

:   Stores the original information of the C type that was present in the C header
    (except the mutability of it which is stored here in the `mutable` field).
    This is important for the C part of the binding.

    See [CType](../ctype).

`get_size_func` (<span class="nullable">Nullable</span>)

:   If not `#!json null`, this is a C function (stored in the `cname`) that should be
    called first to know how much memory to allocate for this type. The binding should
    prevent from the client the necessity of calling this function by doing this already
    and returning the buffer without the overhead of its size. In typical high level
    languages, the size of the array will be stored automatically in the object of the array.
    
    See [IRFunction](../function).

`set_size_func` (<span class="nullable">Nullable</span>)

:   If not `#!json null`, this is a C function (stored in the `cname`) that should be
    called (with the size of this buffer) after invoking the associated function of
    this type.

    See [IRFunction](../function).
