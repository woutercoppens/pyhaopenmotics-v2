import itertools
from collections import defaultdict
from typing import List

# def merge(shared_key, *iterables):
#     result = defaultdict(dict)
#     for dictionary in itertools.chain.from_iterable(iterables):
#         result[dictionary[shared_key]].update(dictionary)
#     # for dictionary in result.values():
#     #     dictionary.pop(shared_key)
#     return result

# def merge(shared_key: str, list_a: list, list_b: list):

#     result = []
#     for x in list_a:
#         for y in list_b:
#             if x[shared_key] == y[shared_key]:
#                 x.update(y)
#                 result.append(x)

#     return result


def get_key_for_word(dictionary, word):
    try:
        for key, value in dictionary.items():
            if value == word:
                return key
        return None

    except KeyError as er:
        _LOGGER.error(er)
        return None


def merge_dicts(list_a: list, dkey: str, list_b: list):
    """Merges list_b into the key 'dkey' of list_a.

    2 list are given:
    list_a = [{'name': 'Vijver', 'room': 255, 'module_type': 'O', 'id': 0},
             {'name': 'Boom', 'room': 255, 'module_type': 'O', 'id': 1}]
    list_b = [{'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 0, 'locked': False},
             {'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 1, 'locked': False}]
    The dictionaries in list_b are merged under the key 'dkey' into the
    disctionaries of list_a
    result = [{'name': 'Vijver', 'room': 255, 'module_type': 'O', 'id': 0,
                'status': {'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 0, 'locked': False}},
              {'name': 'Boom', 'room': 255, 'module_type': 'O', 'id': 1,
              status': {'status': 0, 'dimmer': 100, 'ctimer': 0, 'id': 1, 'locked': False}}]
    """
    result = [d1 | {dkey: d2} for d1, d2 in zip(list_a, list_b)]
    return result
