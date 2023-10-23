from typing import List, Tuple


def add_extension(file_path: str, extension: str) -> str:
    if not file_path.lower().endswith(extension.lower()):
        if "." in file_path:
            raise ValueError("File path already has a different extension")
        file_path += f".{extension}"
    return file_path


def join_string_with_commas(strings: List[str], joiner="and") -> str:
    str_out = ""
    if len(strings) > 0:
        str_out = strings[0]
        for s in strings[1:-1]:
            str_out += ", " + s
        if len(strings) > 1:
            str_out += f" {joiner} " + strings[-1]
    return str_out


def shape_to_string(shape: List[int]) -> str:
    if not isinstance(shape, list):
        raise TypeError(
            f"Expected shape to be a list, but it is of type {type(shape)}."
        )
    if not all([isinstance(s, int) for s in shape]):
        raise TypeError(
            f"Expected all elements of shape to be integers, but they are of types {[type(s) for s in shape]}."
        )
    return "[" + "x".join([str(s) for s in shape]) + "]"
