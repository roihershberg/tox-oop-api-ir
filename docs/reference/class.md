# IRClass

```json
{
  "object_name": "IRClass",
  "name": string,
  "is_callback": boolean,
  "handle": "[IRNativeHandle](../native_handle) | [IRNumberHandle](../number_handle)",
  "default_init": "[IRFunction](../function)",
  "properties": "[[IRProperty](../property), ...]",
  "functions": "[[IRFunction](../function), ...]",
  "inner_classes": "[[IRClass](../class), ...]"
}
```

`name`

:   The name of the class.
    
    E.g. `#!json "Tox"`

`is_callback`

:   If `#!json true`, this signifies that the class is a callback and should be represented as a
    lambda or functional interface depending on the language. The class will have only one function
    called `callback`.

`handle` (<span class="nullable">Nullable</span>)

:   If not `#!json null`, the handle signifies that the class is wrapping
    a certain handle (either a pointer or a number) that should exist as a private field of the class.
    The handle IR objects specify special handling of that handle.

    Possible types: [IRNativeHandle](../native_handle) or [IRNumberHandle](../number_handle).

`default_init` (<span class="nullable">Nullable</span>)

:   If not `#!json null`, this is a function that represents a C function that should be called
    when the object is constructed.

    See [IRFunction](../function).

`properties`

:   The list of properties the class contains. See [IRProperty](../property).

`functions`

:   The list of functions the class contains. See [IRFunction](../function).

`inner_classes`

:   The list of inner classes (IRClass) the class contains.
    
    Each inner class should have access to its parents and their handles.
    This implies that a non-static function of an inner class should first pass to the corresponding C function
    every handle of its parents in order of hierarchy and then any other parameters of the function.

    Example:

    ``` mermaid
    graph TD
      tox[Tox] --> friend[Friend];
      friend --> file["File<br><br>send_chunk(...)"];
    ```
    
    When the `send_chunk` function is called the call of the C function should be as follows
    (handle access is simplified for representation):
    ```cpp
    tox_file_send_chunk(Tox::handle, Friend::handle, File::handle, ...);
    ```
