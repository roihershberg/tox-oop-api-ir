# IREnum

```json
{
  "object_name": "IREnum",
  "name": string,
  "cname": string,
  "values": "[[IREnumValue](../enum_value), ...]"
}
```

`name`

:   The name of the enum.
    
    E.g. `#!json "ToxUserStatus"`

`cname`

:   The original name of the enum that was present in the C header.
    
    E.g. `#!json "Tox_User_Status"`

`values`

:   The list of enum values. See [IREnumValue](../enum_value).
