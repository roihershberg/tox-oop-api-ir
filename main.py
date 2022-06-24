from pyclibrary import CParser
from parsing_to_ir import *
from download_headers import download_headers
from typing import List, Union
import argparse
import json
import re
import os

IR_VERSION = '0.1.0'
TOX_VERSION = '0.2.18'

HEADERS_DIR = 'tox_headers'
OUTPUT_DIR = 'output'
OUTPUT_FILENAME = 'tox_oop_api_ir'

NATIVE_ALLOCATE_FUNC_NAME = 'allocate_native'
NATIVE_DEALLOCATE_FUNC_NAME = 'deallocate_native'

GETTER_SEARCH_KEYWORD = 'get_'
SETTER_SEARCH_KEYWORD = 'set_'


# https://stackoverflow.com/a/1118038
def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


def get_all_ir_classes(ir_classes: List[IRClass]) -> List[IRClass]:
    all_ir_classes: List[IRClass] = [ir_class for ir_class in ir_classes]
    for ir_class in ir_classes:
        all_ir_classes.extend(get_all_ir_classes(ir_class.inner_classes))

    return all_ir_classes


def convert_functions_error_code_to_exception(ir_functions: List[IRFunction], ir_exceptions: List[IRException]):
    # Convert functions' error param to exception throwing
    for func in ir_functions:
        error_params: List[Union[IRParam, IRBufferWrapper]] = [param for param in func.params if param.name == 'error']
        if error_params:
            error_param: IRParam = error_params[0]
            error_ir_enum_name: str = error_param.type.name
            possible_ir_exceptions: List[IRException] = [
                ir_exception for ir_exception in ir_exceptions if ir_exception.enum_name == error_ir_enum_name
            ]
            if possible_ir_exceptions:
                ir_exception = possible_ir_exceptions[0]
                func.params.remove(error_param)
                func.throws = ir_exception.name
            else:
                raise RuntimeError(f'Could not find appropriate exception class for the enum "{error_ir_enum_name}"')


def require_class(ir_class_name: str, ir_classes: List[IRClass]) -> IRClass:
    found_ir_classes: List[IRClass] = [ir_class for ir_class in ir_classes if ir_class.name == ir_class_name]
    if found_ir_classes:
        return found_ir_classes[0]
    else:
        new_class = IRClass(ir_class_name)
        ir_classes.append(new_class)
        return new_class


def move_struct_alloc_functions_to_class(
        ir_functions: List[IRFunction],
        ir_classes: List[IRClass],
        known_structs: List[str]
):
    for func in [func for func in ir_functions]:
        return_type: IRType = func.return_type.type
        return_type_ctype_name: str = return_type.ctype.name
        optimized_return_type_ctype_name = optimize_ctype_name(return_type_ctype_name)
        if optimized_return_type_ctype_name in known_structs and 'new' in func.name:
            func.name = NATIVE_ALLOCATE_FUNC_NAME
            func.is_static = True
            ir_class = require_class(return_type.name, ir_classes)
            if not ir_class.handle:
                ir_class.handle = IRNativeHandle()
            ir_functions.remove(func)
            ir_class.handle.alloc_func = func


def move_struct_functions_to_class(ir_functions: List[IRFunction], ir_classes: List[IRClass], known_structs: List[str]):
    for func in [func for func in ir_functions]:
        if func.params:
            first_param: IRParam = func.params[0]
            first_param_ctype_name: str = first_param.type.ctype.name
            optimized_first_param_ctype_name = optimize_ctype_name(first_param_ctype_name)
            if optimized_first_param_ctype_name in known_structs:
                if 'free' in func.name or 'kill' in func.name:
                    func.name = NATIVE_DEALLOCATE_FUNC_NAME
                    func.is_static = True
                    ir_class = require_class(first_param.type.name, ir_classes)
                    if not ir_class.handle:
                        ir_class.handle = IRNativeHandle()
                    ir_functions.remove(func)
                    ir_class.handle.dealloc_func = func
                else:
                    func.params.remove(first_param)
                    ir_class = require_class(first_param.type.name, ir_classes)
                    ir_functions.remove(func)
                    ir_class.functions.append(func)


def move_leftover_functions_to_base_class(base_class: str, ir_functions: List[IRFunction], ir_classes: List[IRClass]):
    for func in ir_functions:
        func.is_static = True

    ir_class = require_class(base_class, ir_classes)
    ir_class.functions.extend(ir_functions)
    ir_functions.clear()


# https://stackoverflow.com/a/1176023
def pascal_case_to_snake_case(ir_class_name: str) -> str:
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', ir_class_name).lower()


def optimize_functions_name_in_classes(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in ir_class.functions:
            prefix = pascal_case_to_snake_case(ir_class.name) + '_'
            if func.name.startswith(prefix):
                func.name = func.name[len(prefix):]


def is_size_func_name(func_name: str) -> bool:
    return func_name.endswith('_size') or func_name.endswith('_length')


def search_buffer_size_func(keyword: str, ir_class: IRClass, ir_classes: List[IRClass]) -> Optional[IRFunction]:
    # Search for size functions in the same class
    for func in ir_class.functions:
        if keyword in func.name and is_size_func_name(func.name):
            return func

    # Search for static size functions in other classes
    for clazz in ir_classes:
        for func in clazz.functions:
            if func.is_static and keyword in func.name and is_size_func_name(func.name):
                return func
        for ir_property in clazz.properties:
            if ir_property.is_static and keyword in ir_property.name and is_size_func_name(ir_property.name):
                return ir_property.getter

    return None


def is_ir_type_of_string(ir_type: IRType) -> bool:
    return ir_type.name == 'char' and ir_type.is_array


def set_buffer_size_func_to_return_types(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in [func for func in ir_class.functions]:
            if (
                    func.return_type.type.is_array and not is_ir_type_of_string(func.return_type.type)
                    and not func.return_type.replaced
            ) or (
                    func.return_type.type.ctype.is_pointer
                    and 'event' in func.cname
                    and func.return_type.type.name != 'ToxEvents'
            ):
                keyword = func.name[func.name.find(GETTER_SEARCH_KEYWORD) + len(GETTER_SEARCH_KEYWORD):]
                if keyword == 'savedata_data':
                    keyword = 'savedata'
                elif ir_class.name == 'ToxEventFileRecvChunk' and func.name == 'get_data':
                    keyword = ''
                size_func = search_buffer_size_func(keyword, ir_class, ir_classes)
                if not size_func:
                    raise RuntimeError(f'Could not find size getter function for the keyword "{keyword}"')
                if GETTER_SEARCH_KEYWORD in size_func.name and size_func in ir_class.functions:
                    ir_class.functions.remove(size_func)
                func.return_type.type.get_size_func = size_func


def optimize_buffer_getters(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in [func for func in ir_class.functions]:
            if GETTER_SEARCH_KEYWORD in func.name or func.name == 'hash':
                if func.return_type.type.name == 'void' or func.return_type.type.name == 'bool':
                    for param_index, ir_param in enumerate(func.params):
                        if ir_param.type.is_array:
                            keyword = func.name[func.name.find(GETTER_SEARCH_KEYWORD) + len(GETTER_SEARCH_KEYWORD):]
                            if keyword == 'dht_id':  # Manual handling
                                keyword = 'address'
                            elif keyword == 'id':
                                keyword = '_id'
                            elif func.name == 'hash':
                                keyword = 'hash'
                            size_func = search_buffer_size_func(keyword, ir_class, ir_classes)
                            if not size_func:
                                raise RuntimeError(f'Could not find size getter function for the keyword "{keyword}"')
                            if GETTER_SEARCH_KEYWORD in size_func.name and size_func in ir_class.functions:
                                ir_class.functions.remove(size_func)  # The function is specific to only one property
                            ir_param.type.get_size_func = size_func
                            # Convert the param to be returned
                            func.params.remove(ir_param)
                            func.return_type.replaced = func.return_type.type
                            func.return_type.type = ir_param.type
                            func.return_type.param_index = param_index
                            break


def optimize_buffer_setters(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in ir_class.functions:
            if SETTER_SEARCH_KEYWORD in func.name and func.return_type.type.name == 'void':
                for ir_param in func.params:
                    if type(ir_param) == IRParam and ir_param.type.is_array:
                        keyword = func.name[func.name.find(SETTER_SEARCH_KEYWORD) + len(SETTER_SEARCH_KEYWORD):]
                        if keyword == 'savedata_data':  # Manual handling
                            keyword = 'savedata'
                        size_func = search_buffer_size_func(keyword, ir_class, ir_classes)
                        if size_func:
                            if SETTER_SEARCH_KEYWORD in size_func.name and size_func in ir_class.functions:
                                ir_class.functions.remove(size_func)  # The function is specific to only one property
                            ir_param.type.set_size_func = size_func
                            break


def set_buffer_size_func_to_params(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in ir_class.functions:
            for ir_param in func.params:
                if type(ir_param) == IRParam and ir_param.type.is_array and not ir_param.type.get_size_func:
                    size_func = search_buffer_size_func(ir_param.name, ir_class, ir_classes)
                    if size_func:
                        ir_param.type.get_size_func = size_func


def manual_buffer_size_func(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in ir_class.functions:
            if func.name == 'conference_by_id':
                keyword = '_id'
            elif func.name == 'conference_by_uid':
                keyword = '_uid'
            else:
                continue

            for ir_param in func.params:
                if ir_param.type.is_array:
                    size_func = search_buffer_size_func(keyword, ir_class, ir_classes)
                    if size_func:
                        ir_param.type.get_size_func = size_func
                        break


def add_callbacks(callbacks: List[IRFunction], ir_classes: List[IRClass]):
    for callback in callbacks:
        callback_class = require_class(snake_case_to_pascal_case(callback.name), ir_classes)
        callback_class.is_callback = True
        callback.name = 'callback'
        callback_class.functions.append(callback)


def wrap_buffer_parameters(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in ir_class.functions:
            new_params: List[Union[IRParam, IRBufferWrapper]] = []
            skip_param = False
            for index, ir_param in enumerate(func.params):
                if skip_param:
                    skip_param = False
                    continue
                if index + 1 < len(func.params):
                    possible_length_param = func.params[index + 1]
                    if ir_param.type.is_array and not ir_param.type.get_size_func \
                            and 'length' in possible_length_param.name:
                        new_params.append(IRBufferWrapper(ir_param, possible_length_param))
                        skip_param = True
                    else:
                        new_params.append(ir_param)
                else:
                    new_params.append(ir_param)
            func.params.clear()
            func.params.extend(new_params)


def change_param_to_number_handle_wrapper(ir_param: IRParam, new_name: str, new_type_name: str):
    ir_param.name = new_name
    ir_param.type.name = new_type_name
    ir_param.type.contains_number_handle = True


def move_number_holders_functions_to_inner_classes(ir_classes: List[IRClass]) -> bool:
    found = False
    for ir_class in ir_classes:
        for func in [func for func in ir_class.functions]:
            matches = [
                ir_param for ir_param in func.params if type(ir_param) == IRParam and ir_param.name.endswith('_number')
            ]
            if matches:
                found = True
                param_match = matches[0]
                class_snake_case_name = param_match.name.replace('_number', '')
                ir_class_name = snake_case_to_pascal_case(class_snake_case_name)
                if func.name == 'peer_number_is_ours':
                    change_param_to_number_handle_wrapper(
                        param_match,
                        new_name=class_snake_case_name,
                        new_type_name=ir_class_name,
                    )
                elif func.name == 'conference_invite' and ir_class.name == 'Friend':
                    change_param_to_number_handle_wrapper(
                        param_match,
                        new_name=class_snake_case_name,
                        new_type_name=ir_class_name,
                    )
                else:
                    num_holder_class = require_class(ir_class_name, ir_class.inner_classes)
                    if not num_holder_class.handle:
                        num_holder_class.handle = IRNumberHandle(param_match.type)
                    func.params.remove(param_match)
                    ir_class.functions.remove(func)
                    num_holder_class.functions.append(func)

    return found


def convert_leftover_number_handle_function_params_to_wrappers(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in ir_class.functions:
            matches = [
                ir_param for ir_param in func.params if type(ir_param) == IRParam and ir_param.name.endswith('_number')
            ]
            for param_match in matches:
                class_snake_case_name = param_match.name.replace('_number', '')
                ir_class_name = snake_case_to_pascal_case(class_snake_case_name)
                change_param_to_number_handle_wrapper(
                    param_match,
                    new_name=class_snake_case_name,
                    new_type_name=ir_class_name,
                )


def manual_handling_of_functions_returning_number_handle(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in ir_class.functions:
            if func.name == 'self_get_friend_list' \
                    or func.name == 'friend_add' \
                    or func.name == 'friend_add_norequest' \
                    or func.name == 'friend_by_public_key':
                func.return_type.type.name = 'Friend'
                func.return_type.type.contains_number_handle = True
            elif func.name == 'conference_get_chatlist' \
                    or func.name == 'conference_new' \
                    or func.name == 'conference_by_id' \
                    or func.name == 'conference_by_uid' \
                    or func.name == 'conference_join':
                func.return_type.type.name = 'Conference'
                func.return_type.type.contains_number_handle = True
            elif func.name == 'file_send':
                func.return_type.type.name = 'File'
                func.return_type.type.contains_number_handle = True


def manual_handling_of_functions(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        if ir_class.name == 'ToxOptions':
            for func in [func for func in ir_class.functions]:
                if func.name == 'default':
                    ir_class.functions.remove(func)
                    ir_class.default_init = func


def get_function_by_name(func_name: str, functions: List[IRFunction]) -> Optional[IRFunction]:
    for func in functions:
        if func.name == func_name:
            return func
    return None


def convert_getters_setters_to_properties(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in [func for func in ir_class.functions]:
            if GETTER_SEARCH_KEYWORD in func.name and not func.params:
                property_name = func.name.replace(GETTER_SEARCH_KEYWORD, '')
                setter_func_name = func.name.replace(GETTER_SEARCH_KEYWORD, SETTER_SEARCH_KEYWORD)
                func.name = 'get'
                ir_property = IRProperty(property_name)
                ir_property.getter = func
                setter_func = get_function_by_name(setter_func_name, ir_class.functions)
                if setter_func and len(setter_func.params) == 1:
                    setter_func.name = 'set'
                    ir_property.setter = setter_func
                ir_class.functions.remove(func)
                ir_class.properties.append(ir_property)
        setters_still_in_functions = [setter for setter in ir_class.functions if setter.name == 'set']
        for setter in setters_still_in_functions:
            ir_class.functions.remove(setter)


def remove_bool_return_type_if_throws_exception(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in ir_class.functions:
            if func.return_type.type.name == 'bool' and func.throws:
                func.return_type.replaced = func.return_type.type
                func.return_type.type = IRType('void', True, False, CType('void', False))


def convert_static_empty_params_functions_to_properties(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in [func for func in ir_class.functions]:
            if func.is_static and not func.params:
                property_name = func.name.replace(GETTER_SEARCH_KEYWORD, '')
                func.name = 'get'
                ir_property = IRProperty(property_name)
                ir_property.getter = func
                ir_property.is_static = True
                ir_class.functions.remove(func)
                ir_class.properties.append(ir_property)


def manual_converting_of_functions_to_properties(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for func in [func for func in ir_class.functions]:
            if func.name == 'iteration_interval':
                property_name = func.name
                func.name = 'get'
                ir_property = IRProperty(property_name)
                ir_property.getter = func
                ir_class.functions.remove(func)
                ir_class.properties.append(ir_property)


rename_map = {
    'Tox': {
        'properties': {},
        'functions': {
            'friend_add': 'add_friend',
            'friend_add_norequest': 'add_friend_norequest',
            'conference_new': 'new_conference',
        },
    },
    'Friend': {
        'properties': {},
        'functions': {
            'file_send': 'send_file',
        },
    },
    'File': {
        'properties': {
            'file_id': 'id',
        },
        'functions': {},
    },
    'Conference': {
        'properties': {},
        'functions': {
            'peer_number_is_ours': 'peer_is_ours',
        },
    },
}


def manual_rename(ir_classes: List[IRClass]):
    for ir_class in ir_classes:
        for class_name, rename_spec in rename_map.items():
            for property_name, new_property_name in rename_spec['properties'].items():
                for ir_property in ir_class.properties:
                    if ir_property.name == property_name:
                        ir_property.name = new_property_name
            for func_name, new_func_name in rename_spec['functions'].items():
                for func in ir_class.functions:
                    if func.name == func_name:
                        func.name = new_func_name


def main():
    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Generate an Intermediate Representation of a Tox OOP API from c-toxcore.\n\n'
                    f'Make sure the Tox headers are in a {HEADERS_DIR} directory. Otherwise download '
                    'them with the --download-headers option.')
    arg_parser.add_argument('--download-headers', action='store_true',
                            help='download the Tox headers from the version this script supports')

    if not os.path.exists(HEADERS_DIR):
        os.mkdir(HEADERS_DIR)

    supported_headers_and_base_class = {
        'tox.h': 'Tox',
    }

    args = arg_parser.parse_args()
    if args.download_headers:
        headers_to_download = ['toxcore/tox.h']
        download_headers(HEADERS_DIR, 'v' + TOX_VERSION, headers_to_download)

    ir_enums: List[IREnum] = []
    ir_exceptions: List[IRException] = []
    ir_classes: List[IRClass] = []

    headers = [header for header in os.listdir(HEADERS_DIR) if header.endswith('.h')]
    if not headers:
        print(f'There are no headers in the {HEADERS_DIR} folder. Make sure to download them either with the '
              '--download-headers option or manually.')
        exit(1)
    for header in headers:
        if header not in supported_headers_and_base_class.keys():
            print(f'The header {header} is not supported. Please remove it from the {HEADERS_DIR} directory.')
            exit(1)
        header_file = f'{HEADERS_DIR}/{header}'
        parser = CParser(header_file, cache=f'{header_file}.cache')
        defs: dict = parser.file_defs[header]

        # Parse enums
        enums_defs: dict = defs['enums']
        header_ir_enums: List[IREnum] = parse_enums(enums_defs)
        ir_enums.extend(header_ir_enums)

        # Create exceptions when the enums represent errors (name starts with 'ToxErr')
        error_ir_enums = filter(lambda ir_enum: ir_enum.name.startswith('ToxErr'), ir_enums)
        header_ir_exceptions: List[IRException] = list(map(
            lambda ir_enum: IRException(
                name=ir_enum.name.replace('ToxErr', 'Tox'),
                enum_name=ir_enum.name
            ),
            error_ir_enums,
        ))
        ir_exceptions.extend(header_ir_exceptions)

        # Parse functions to IR as they are
        functions_defs: dict = defs['functions']
        ir_functions: List[IRFunction] = parse_functions(functions_defs)
        ir_functions = [ir_function for ir_function in ir_functions if 'operating_system' not in ir_function.name]

        convert_functions_error_code_to_exception(ir_functions, ir_exceptions)

        known_structs = list(defs['structs'].keys())

        # Move struct allocation functions (return type is a struct and name contains 'new') to the corresponding classes
        move_struct_alloc_functions_to_class(ir_functions, ir_classes, known_structs)

        # Move struct functions (first parameter is a struct) to the corresponding classes
        move_struct_functions_to_class(ir_functions, ir_classes, known_structs)

        move_leftover_functions_to_base_class(supported_headers_and_base_class[header], ir_functions, ir_classes)

        # Remove class name as the prefix of the functions
        optimize_functions_name_in_classes(ir_classes)

        found_number_holders_functions = True
        while found_number_holders_functions:
            # Move functions that their currently first parameter name ends with '_number'
            # to an inner class that should contain that parameter as a field
            found_number_holders_functions = move_number_holders_functions_to_inner_classes(
                get_all_ir_classes(ir_classes))

            # Remove class name as the prefix of the functions
            optimize_functions_name_in_classes(get_all_ir_classes(ir_classes))

        callbacks_defs = {type_name: type_def for type_name, type_def in defs['types'].items() if
                          type_name.endswith('_cb')}
        callback_functions: List[IRFunction] = parse_functions(callbacks_defs)
        add_callbacks(callback_functions, ir_classes)

        convert_leftover_number_handle_function_params_to_wrappers(get_all_ir_classes(ir_classes))

        set_buffer_size_func_to_return_types(get_all_ir_classes(ir_classes))

        optimize_buffer_getters(get_all_ir_classes(ir_classes))
        optimize_buffer_setters(get_all_ir_classes(ir_classes))

        manual_buffer_size_func(get_all_ir_classes(ir_classes))

        wrap_buffer_parameters(get_all_ir_classes(ir_classes))

        set_buffer_size_func_to_params(get_all_ir_classes(ir_classes))

        manual_handling_of_functions_returning_number_handle(get_all_ir_classes(ir_classes))
        manual_handling_of_functions(get_all_ir_classes(ir_classes))

        convert_getters_setters_to_properties(get_all_ir_classes(ir_classes))

        remove_bool_return_type_if_throws_exception(get_all_ir_classes(ir_classes))

        convert_static_empty_params_functions_to_properties(get_all_ir_classes(ir_classes))

        manual_converting_of_functions_to_properties(get_all_ir_classes(ir_classes))

        manual_rename(get_all_ir_classes(ir_classes))

    # Construct final JSON
    root = {
        'ir_version': IR_VERSION,
        'tox_version': TOX_VERSION,
        'enums': todict(ir_enums),
        'exceptions': todict(ir_exceptions),
        'classes': todict(ir_classes),
    }
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    with open(f'{OUTPUT_DIR}/{OUTPUT_FILENAME}.json', 'w') as f:
        f.write(json.dumps(root))


if __name__ == '__main__':
    main()
