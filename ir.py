from typing import List, Optional, Union


class IRObject:
    def __init__(self):
        self.object_name = self.__class__.__name__


class CType(IRObject):
    def __init__(self, name: str, is_pointer: bool):
        super().__init__()
        self.name = name
        self.is_pointer = is_pointer


class IRType(IRObject):
    def __init__(self, name: str, mutable: bool, is_array: bool, ctype: CType):
        super().__init__()
        self.name = name
        self.mutable = mutable
        self.is_array = is_array
        self.acts_as_string = False
        self.contains_number_handle = False
        self.ctype = ctype
        self.get_size_func: Optional[IRFunction] = None
        self.set_size_func: Optional[IRFunction] = None


class IRParam(IRObject):
    def __init__(self, name: str, param_type: IRType):
        super().__init__()
        self.name = name
        self.type = param_type


class IRBufferWrapper(IRObject):
    def __init__(self, buffer_param: IRParam, length_param: IRParam):
        super().__init__()
        self.buffer_param = buffer_param
        self.length_param = length_param


class IRReturnType(IRObject):
    def __init__(self, return_type: IRType):
        super().__init__()
        self.type = return_type
        self.replaced: Optional[IRType] = None


class IRFunction(IRObject):
    def __init__(self, name: str, cname: str, return_type: IRReturnType, params: List[Union[IRParam, IRBufferWrapper]]):
        super().__init__()
        self.name = name
        self.cname = cname
        self.return_type = return_type
        self.throws: Optional[str] = None
        self.is_static = False
        self.params = params


class IRProperty(IRObject):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.is_static = False
        self.getter: Optional[IRFunction] = None
        self.setter: Optional[IRFunction] = None


class IREnumValue(IRObject):
    def __init__(self, name: str, cname: str, ordinal: int):
        super().__init__()
        self.name = name
        self.cname = cname
        self.ordinal = ordinal


class IREnum(IRObject):
    def __init__(self, name: str, cname: str, values: List[IREnumValue]):
        super().__init__()
        self.name = name
        self.cname = cname
        self.values = values


class IRException(IRObject):
    def __init__(self, name: str, enum_name: str):
        super().__init__()
        self.name = name
        self.enum_name = enum_name


class IRNativeHandle(IRObject):
    def __init__(self):
        super().__init__()
        self.alloc_func: Optional[IRFunction] = None
        self.dealloc_func: Optional[IRFunction] = None


class IRNumberHandle(IRObject):
    def __init__(self, ir_type: IRType):
        super().__init__()
        self.type = ir_type


class IRClass(IRObject):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.is_callback = False
        self.handle: Union[IRNativeHandle, IRNumberHandle, None] = None
        self.default_init: Optional[IRFunction] = None
        self.properties: List[IRProperty] = []
        self.functions: List[IRFunction] = []
        self.inner_classes: List[IRClass] = []
