"""
Code for serializing and deserializing the custom classes.
"""
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields, is_dataclass
import inspect
import json

import dmtoolkit.api.models

_MODELS: dict[str, type] = {}

def _get_models() -> dict[str, type]:
    """Returns a mapping of model names to their classes. Used to map __dataclass_ fields from
    serialized objects to their appropriate Python class."""
    # Lazy-load models
    if not _MODELS:
        for name, obj in inspect.getmembers(dmtoolkit.api.models):
            if is_dataclass(obj):
                _MODELS[name] = obj
    return _MODELS


def _asdict_inner(o: dataclass) -> dict:
    data = o.__dict__
   
    field_types = {field.name: field.type for field in fields(o.__class__)}
    delfields = []
    for field, val in data.items():
        # Check if optional
        field_type = field_types.get(field)
        if not field_type:
            continue
        if field_type.startswith("Optional["):
            if val is None or (hasattr(val, "__iter__") and len(val) == 0):
                delfields.append(field)
    for field in delfields:
        del data[field]

    return data | { "__dataclass__": type(o).__name__}

def _asdict(obj: dataclass):
    """Custom asdict that removed optional fields which are null."""
    if isinstance(obj, Sequence):
        return type(obj)(*[_asdict(x) for x in obj])
    if isinstance(obj, Mapping):
        return type(obj)(**{k: _asdict(v) for k, v in obj.items()})
    if is_dataclass(obj):
        return _asdict_inner(obj)
    return obj


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return _asdict(o)
        return super().default(o)


class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, o: dict):
        if class_name := o.pop("__dataclass__", None):
            if class_name:
                models = _get_models()
                class_ = models.get(class_name)
                if not class_:
                    raise ValueError(f"Unknown dataclass '{class_name}'")
                return class_(**o)
        return o


def load_json(fp, *, parse_float=None,
        parse_int=None, parse_constant=None, **kw):
    """Deserialize ``fp`` (a ``.read()``-supporting file-like object containing a JSON document) to
    a Python object.
    """
    return json.load(
        fp,
        cls=CustomDecoder,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant
    )


def dump_json(obj, fp, *, skipkeys=False, ensure_ascii=True, check_circular=True,
        allow_nan=True, indent=2, separators=None,
        default=None, sort_keys=False, **kw):
    """Serialize ``obj`` as a JSON formatted stream to ``fp`` (a
    ``.write()``-supporting file-like object).

    If ``skipkeys`` is true then ``dict`` keys that are not basic types
    (``str``, ``int``, ``float``, ``bool``, ``None``) will be skipped
    instead of raising a ``TypeError``.

    If ``ensure_ascii`` is false, then the strings written to ``fp`` can
    contain non-ASCII characters if they appear in strings contained in
    ``obj``. Otherwise, all such characters are escaped in JSON strings.

    If ``check_circular`` is false, then the circular reference check
    for container types will be skipped and a circular reference will
    result in an ``RecursionError`` (or worse).

    If ``allow_nan`` is false, then it will be a ``ValueError`` to
    serialize out of range ``float`` values (``nan``, ``inf``, ``-inf``)
    in strict compliance of the JSON specification, instead of using the
    JavaScript equivalents (``NaN``, ``Infinity``, ``-Infinity``).

    If ``indent`` is a non-negative integer, then JSON array elements and
    object members will be pretty-printed with that indent level. An indent
    level of 0 will only insert newlines. ``None`` is the most compact
    representation.

    If specified, ``separators`` should be an ``(item_separator, key_separator)``
    tuple.  The default is ``(', ', ': ')`` if *indent* is ``None`` and
    ``(',', ': ')`` otherwise.  To get the most compact JSON representation,
    you should specify ``(',', ':')`` to eliminate whitespace.

    ``default(obj)`` is a function that should return a serializable version
    of obj or raise TypeError. The default simply raises TypeError.

    If *sort_keys* is true (default: ``False``), then the output of
    dictionaries will be sorted by key.
    """
    return json.dump(
        obj,
        fp,
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        cls = CustomEncoder,
        indent=indent,
        separators=separators,
        default=default,
        sort_keys=sort_keys
    )