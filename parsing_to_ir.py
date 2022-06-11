from typing import Dict
from ir import *


def optimize_ctype_name(ctype_name: str) -> str:
    return ctype_name.replace('struct ', '')


primitives_ctype_ir_map: Dict[str, str] = {
    'uint8_t': 'byte',
    'uint16_t': 'ushort',
    'uint32_t': 'uint',
    'uint64_t': 'ulong',
    'size_t': 'ulong',
    'char': 'char',
    'bool': 'bool',
    'void': 'void',
}


def snake_case_to_pascal_case(string: str) -> str:
    words: List[str] = string.split('_')
    words_pascal_cased: List[str] = list(map(lambda word: word[0].upper() + word[1:], words))
    return "".join(words_pascal_cased)


def get_ir_type_from_ctype(ctype: CType, mutable: bool) -> IRType:
    optimized_ctype_name: str = optimize_ctype_name(ctype.name)

    if optimized_ctype_name in primitives_ctype_ir_map:
        ir_type_name: str = primitives_ctype_ir_map[optimized_ctype_name]
        if ir_type_name == 'void':
            is_array = False
        else:
            is_array = ctype.is_pointer
        return IRType(ir_type_name, mutable, is_array, ctype)
    else:
        ir_type_name: str = snake_case_to_pascal_case(optimized_ctype_name)
        return IRType(ir_type_name, mutable, is_array=False, ctype=ctype)


def parse_type(cparser_type) -> IRType:
    is_pointer = False
    mutable = True

    if type(cparser_type) == str:
        ctype_name = cparser_type
    else:
        ctype_name = cparser_type.type_spec
        ctype_declerators = cparser_type.declarators

        if ctype_declerators:
            is_pointer = ctype_declerators[0] == '*'

        for type_qual in cparser_type.type_quals[0]:
            if type_qual == 'const':
                mutable = False

    return get_ir_type_from_ctype(CType(ctype_name, is_pointer), mutable)


def parse_functions(functions_defs: dict) -> List[IRFunction]:
    functions: List[IRFunction] = []

    for func_name, func_def in functions_defs.items():
        return_type = func_def.type_spec
        declarators = func_def.declarators[0]

        params = []
        empty = declarators[0][1].type_spec == 'void' and not declarators[0][0]
        if not empty:
            for param_name, param_type, _ in declarators:
                ir_param_type: IRType = parse_type(param_type)

                # Check if the type acts as a string
                possible_substrings = ['name', 'title', 'message']
                if any((substring in param_name and ir_param_type.ctype.name == 'uint8_t' and ir_param_type.is_array)
                       for substring in possible_substrings):
                    ir_param_type.acts_as_string = True

                params.append(IRParam(param_name, ir_param_type))

        functions.append(IRFunction(func_name, func_name, return_type=parse_type(return_type), params=params))

    return functions


def parse_enums(enums_defs: dict) -> List[IREnum]:
    enums: List[IREnum] = []

    for enum_name, enum_values in enums_defs.items():
        ir_enum_values: List[IREnumValue] = [
            IREnumValue(name=value_name.replace(enum_name.upper() + '_', ''), cname=value_name, ordinal=value_ordinal)
            for value_name, value_ordinal in enum_values.items()
        ]
        ir_enum_name = enum_name.replace('_', '')
        if enum_name != 'T':  # A weird bug
            enums.append(IREnum(ir_enum_name, enum_name, ir_enum_values))

    return enums
