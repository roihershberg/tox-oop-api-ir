# IREnumValue

```json
{
  "object_name": "IREnumValue",
  "name": string,
  "cname": string,
  "ordinal": int
}
```

`name`

:   The name of the enum value.
    
    E.g. `#!json "NONE"`

`cname`

:   The original name of the enum value that was present in the C header.
    
    E.g. `#!json "TOX_USER_STATUS_NONE"`

`ordinal`

:   The ordinal of the enum value. This can be used to determine the order of the enum values
    as it is in the C header although the order in the `values` list of the enum should already be correct.
    
    E.g. `#!json 0`
