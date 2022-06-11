# Reference

This is the reference to the Intermediate Representation of the Tox Object-Oriented API.

The format used to represent it is JSON.
Below is the root of the JSON and you are welcome to expend any Type and read the reference of it.

```json title="Root"
{
  "ir_version": string,
  "tox_version": string,
  "enums": "[[IREnum](enum), ...]",
  "exceptions": "[[IRException](exception), ...]",
  "classes": "[[IRClass](class), ...]"
}
```

`ir_version`

:   The version of this project of the form `<major>.<minor>.<patch>`.
    
    An increment of `<major>` signifies that API breaking changes have been added
    and an increment of the `<minor>` or `<patch>` signifies that changes have been added
    with backwards compatibility in mind.
    See [Semantic Versioning](https://semver.org/) for more details.
    
    E.g. `#!json "1.1.0"`

`tox_version`

:   The version of [c-toxcore](https://github.com/TokTok/c-toxcore) that this IR is generated for.
    
    E.g. `#!json "0.2.18"`

`enums`

:   List of generated enums. See [IREnum](enum).

`exceptions`

:   List of generated exceptions. See [IRException](exception).

`classes`

:   List of generated classes. See [IRClass](class).
