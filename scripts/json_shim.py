"""
Shim for orjson to mimic Python default json API.
"""

# pylint: disable=no-member
# pylint: disable=unused-argument
import orjson
from typing import Union

def dumps(obj, indent=0, ensure_ascii=False) -> str:
    """
    Serialize `obj` to a JSON formatted `str`.
    
    If you specify `indent` as a number greater than 0,
    indent will be 2 spaces.

    `ensure_ascii` does not do anything because orjson does not
    support this feature. By default, orjson does NOT escape
    utf-8 characters to ascii. It is there for compatibility,
    in case that orjson can't be used or we have to migrate
    json libraries again.
    """
    opt = 0
    if indent > 0:
        opt |= orjson.OPT_INDENT_2
    return orjson.dumps(obj, option=opt).decode()

def loads(s: Union[str, bytes, bytearray]):
    """
    Deserialize `s` (a `str`, `bytes` or `bytearray` instance containing a JSON document)
    to a Python object.
    """
    return orjson.loads(s)

def dump(obj, fp, indent=0):
    """
    Serialize `obj` as a JSON formatted stream to `fp`
    (a `.write()`-supporting file-like object).

    If you specify `indent` as a number greater than 0,
    indent will be 2 spaces.
    """
    opt = 0
    if indent > 0:
        opt |= orjson.OPT_INDENT_2
    fp.write(orjson.dumps(obj, option=opt).decode())

def load(fp):
    """
    Deserialize `fp` (a `.read()`-supporting file-like object containing a JSON document)
    to a Python object.
    """
    return orjson.loads(fp.read())

JSONDecodeError = orjson.JSONDecodeError
