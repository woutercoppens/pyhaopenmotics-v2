"""Asynchronous Python client for the OpenMotics API."""

import logging
from typing import Any
import aiohttp
import asyncio

def get_key_for_word(dictionary: dict[str, Any], word: str) -> Any:
    """Return the key with value.

    Args:
        dictionary: dict
        word: str

    Returns:
        Any
    """
    try:
        for key, value in dictionary.items():
            if value == word:
                return key
        return None

    except KeyError as err:
        logging.error(err)
        return None


def merge_dicts(list_a: list[Any], dkey: str, list_b: list[Any]) -> list[Any]:
    """Merge list_b into the key 'dkey' of list_a.

    Args:
        dkey: str
        list_a: list
        list_b: list

    Returns:
        result: list

    # noqa: E800
    2 list are given:
    list_a = [{'name': 'Vijver', 'room': 255, 'module_type': 'O', 'id': 0},
             {'name': 'Boom', 'room': 255, 'module_type': 'O', 'id': 1}]
    list_b = [{'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 0, 'locked': False},
             {'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 1, 'locked': False}]
    The dictionaries in list_b are merged under the key 'dkey' into the
    dictionaries of list_a
    result = [{'name': 'Vijver', 'room': 255, 'module_type': 'O', 'id': 0,
                'status': {'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 0, 'locked': False}},
              {'name': 'Boom', 'room': 255, 'module_type': 'O', 'id': 1,
              status': {'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 1, 'locked': False}}]
    """
    if len(list_a) == 0:
        return []
    if len(list_b) == 0:
        return list_a
    result = [d1 | {dkey: d2} for d1, d2 in zip(list_a, list_b)]
    return result