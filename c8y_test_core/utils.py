"""Utils"""
from __future__ import annotations

import base64
from typing import List, Set, Any, Tuple
from unittest.mock import Mock

import randomname

from c8y_api.model._base import CumulocityObject


def get_ids(objs: List[CumulocityObject]) -> Set[str]:
    """Isolate the ID from a list of database objects."""
    return {o.id for o in objs}


def isolate_last_call_arg(mock: Mock, name: str, pos: int = None) -> Any:
    """Isolate arguments of the last call to a mock.
    The argument can be specified by name and by position.
    Args:
        mock (Mock): the Mock to inspect
        name (str): Name of the parameter
        pos (int): Position of the parameter
    Returns:
        Value of the call argument
    Raises:
        KeyError if the argument was not given/found by name and the
        position was not given/out of bounds.
    """
    mock.assert_called()
    args, kwargs = mock.call_args
    if name in kwargs:
        return kwargs[name]
    if len(args) > pos:
        return args[pos]
    raise KeyError(
        f"Argument not found: '{name}'. "
        f"Not given explcitely and position ({pos}) out of of bounds."
    )


def isolate_all_call_args(mock: Mock, name: str, pos: int = None) -> List[Any]:
    """Isolate arguments of all calls to a mock.
    The argument can be specified by name and by position.
    Args:
        mock (Mock): the Mock to inspect
        name (str): Name of the parameter
        pos (int): Position of the parameter
    Returns:
        List of value of the call argument
    Raises:
        KeyError if the argument was not given/found by name and the
        position was not given/out of bounds.
    """
    mock.assert_called()
    result = []
    for args, kwargs in mock.call_args_list:
        if name in kwargs:
            result.append(kwargs[name])
        elif len(args) > pos:
            result.append(args[pos])
    if not result:
        raise KeyError(f"Argument not found in any of the calls: '{name}', pos: {pos}.")
    return result


def random_name() -> str:
    """Provide a random name."""
    return RandomNameGenerator.random_name()


class RandomNameGenerator:
    """Provides randomly generated names using a public service."""

    # pylint: disable=too-few-public-methods

    @classmethod
    def random_name(cls, num: int = 3, sep: str = "_") -> str:
        """Generate a readable random name from joined random words.
        Args:
            num (int):  number of random words to concatenate
            sep (str):  concatenation separator
        Returns:
            The generated name
        """
        groups = []
        if num <= 1:
            # only a noun
            groups.append("n/")
        elif num == 2:
            # adjective + noun
            groups.append("a/")
            groups.append("n/")
        else:
            # one verb
            groups.append("v/")

            # use adjectives inbetween
            groups.extend(["a/"] * (num - 2))

            # then one noun
            groups.append("n/")

        return randomname.generate(*groups, sep=sep)


def b64encode(auth_string: str) -> str:
    """Encode a string with base64. This uses UTF-8 encoding."""
    return base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")


def build_auth_string(auth_value: str) -> str:
    """Build a complete auth string from an base64 encoded auth value.
    This detects the type based on the `auth_value` contents, assuming
    that JWT tokens always start with an '{'."""
    auth_type = "BEARER" if auth_value.startswith("ey") else "BASIC"
    return f"{auth_type} {auth_value}"


def _to_csv_str(values, delimiter: str = ","):
    formatted_values = []
    for v in values:
        if isinstance(v, bool):
            formatted_values.append(str(v).lower())
        elif isinstance(v, (int, float)):
            formatted_values.append(str(v))
        else:
            formatted_values.append(f'"{v}"')
    return ",".join(formatted_values)


def to_csv(items: Tuple[str, List[Any]], delimiter: str = ",") -> str:
    """Convert items to csv format

    Arguments:
        items (Tuple[str, List[Any]]): List of items, where the first item
          in tuple is the column name, and the second is a list of values.
        delimiter (str): Field delimiter. Defaults to ","

    Returns:
        str: CSV output
    """
    columns = _to_csv_str([item[0] for item in items], delimiter=delimiter)

    data = [item[1] for item in items]

    item_len = len(data[0])
    data_rows = []
    for i in range(0, item_len):
        data_rows.append(_to_csv_str([item[i] for item in data], delimiter=delimiter))

    return "\n".join([columns, *data_rows])
