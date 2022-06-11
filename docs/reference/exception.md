# IRException

```json
{
  "object_name": "IRException",
  "name": string,
  "enum_name": string
}
```

All error enums are replaced with exceptions containing the corresponding enum.
This implicates that the `error` parameter in functions is removed.

`name`

:   The name of the exception. A proper suffix should be added to this name depending on the convention
    in the language.

    For example, if the value of this field is `#!json "ToxOptionsNew"`, in JVM the name should be
    `ToxOptionsNewException` and in Python it should be `ToxOptionsNewError`.

`enum_name`

:   The name of the error enum contained inside the exception.
    
    E.g. `#!json "ToxErrOptionsNew"`

    !!! note

        This is the name of the newly generated [IREnum](../enum) and not the original name in the C header.
