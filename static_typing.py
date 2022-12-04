import inspect
from typing import Callable, List, Type, Dict, Any


def static_typing(function: Callable) -> Callable:
    data = inspect.getfullargspec(function)

    kwargs_types: Dict[str, Type] = data.annotations.copy()
    if "return" in data.annotations.keys():
        kwargs_types.pop("return")

    for i in kwargs_types.keys():
        if kwargs_types[i] == Any:
            kwargs_types[i] = object

    args_types: List[Type] = []
    for i in data.args:
        args_types.append(kwargs_types.get(i, object))

    return_type: Type = data.annotations.get("return", object)

    def funct(*args, **kwargs):
        for i, f in enumerate(args):
            if not isinstance(f, args_types[i]):
                raise TypeError(f"Argument with pos {i + 1} got wrong type. Expected {args_types[i]}, got {type(f)}")

        for i, f in kwargs:
            if not isinstance(f, kwargs_types[i]):
                raise TypeError(f"Argument '{i}' got wrong type. Expected {kwargs_types[i]}, got {type(f)}")

        var = function(*args, **kwargs)

        if not isinstance(var, return_type):
            raise TypeError(f"Incorrect return type. Expected {return_type}, got {type(var)}")
        return var

    return funct
