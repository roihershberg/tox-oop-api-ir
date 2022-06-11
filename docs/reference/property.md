# IRProperty

```json
{
  "object_name": "IRProperty",
  "name": string,
  "is_static": boolean,
  "getter": "[IRFunction](../function)",
  "setter": "[IRFunction](../function)"
}
```

`name`

:   The name of the property.

    E.g. `#!json "ipv6_enabled"`.

`is_static`

:   If the property is static. This is taken from the getter's `is_static` field.

    See the `is_static` field in [IRFunction](../function).

`getter`

:   The C function from which to get the value. The type of the property is determined from
    the `return_type` of the getter.

    See [IRFunction](../function).

`setter` (<span class="nullable">Nullable</span>)

:   If not `#!json null`, this is the C function that should be called to set the value, otherwise
    the property should be immutable.

    See [IRFunction](../function).
