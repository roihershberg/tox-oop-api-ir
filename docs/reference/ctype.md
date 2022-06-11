# CType

```json
{
  "object_name": "CType",
  "name": string,
  "is_pointer": boolean
}
```

`name`

:   The name of the C type without an asterisk (if it's a pointer).

    E.g. `#!json "uint8_t"`

`is_pointer`

:   If the type is a pointer. Either `#!json true` or `#!json false`.

## Important Notes

The mutability of the type (i.e. `#!c const`) is stored in the
`mutable` field in the containing [IRType](../type) object.
