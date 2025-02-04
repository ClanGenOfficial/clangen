"""
Shim for orjson to mimic Python default json API.
"""

# pylint: disable=no-member
import orjson

def dumps(obj, indent=0):
    """
    Serialize `obj` to a JSON formatted `str`.
    
    If you specify `indent` as a number greater than 0,
    indent will ALWAYS BE 2 SPACES.
    """
    opt = 0
    if indent > 0:
        opt = orjson.OPT_INDENT_2
    return orjson.dumps(obj, option=opt).decode()

def loads(s):
    """
    Deserialize `s` (a `str`, `bytes` or `bytearray` instance containing a JSON document)
    to a Python object.
    """
    return orjson.loads(s)

def dump(obj, fp):
    """
    Serialize `obj` as a JSON formatted stream to `fp`
    (a `.write()`-supporting file-like object).
    """
    return fp.write(orjson.dumps(obj).decode())

def load(fp):
    """
    Deserialize `fp` (a `.read()`-supporting file-like object containing a JSON document)
    to a Python object.
    """
    return orjson.loads(fp.read())

JSONDecodeError = orjson.JSONDecodeError
