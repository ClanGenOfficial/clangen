"""Handles file loading and redirection for modded files."""
import builtins
import io
import pygame
try: import ujson
except ImportError: import json as ujson
from pathlib import Path

def _deep_merge(dict1: dict, dict2: dict) -> dict:
  """Deeply merges two dictionaries, overwriting values in dict1."""
  merged = dict1.copy()
  for key, value in dict2.items():
    if key in dict1:
      if isinstance(value, dict) and isinstance(dict1[key], dict):
        merged[key] = _deep_merge(dict1[key], value)
      else:
        merged[key] = value
    else:
      merged[key] = value
  return merged

def _extend_json(old_path: str, new_path: str) -> io.StringIO:
    """Merges two json files together, removing duplicates and returning the merged item."""
    old_json = ujson.load(Path(old_path).open())
    new_json = ujson.load(Path(new_path).open())
    if isinstance(old_json, list) and isinstance(new_json, list):
        extended_json = list({d["patrol_id"]: d for d in old_json + new_json}.values())
    elif isinstance(old_json, dict) and isinstance(new_json, dict):
        extended_json = _deep_merge(new_json, old_json)
    else: 
        raise ValueError("Both files must be of the same type (list or dict).")

    return io.StringIO(ujson.dumps(extended_json))

def _extend_json_from_memory(old_path: str, new_json: bytes) -> io.StringIO:
    """Merges two json files together, removing duplicates and returning the merged item."""
    old_json = ujson.load(Path(old_path).open())
    new_json = ujson.loads(new_json)
    if isinstance(old_json, list) and isinstance(new_json, list):
        extended_json = list({d["patrol_id"]: d for d in old_json + new_json}.values())
    elif isinstance(old_json, dict) and isinstance(new_json, dict):
        extended_json = _deep_merge(old_json, new_json)
    else: 
        raise ValueError("Both files must be of the same type (list or dict).")
    return io.StringIO(ujson.dumps(extended_json))

class _FileHandler:
    enabled = True
    lookup_table = {}
    memory = {}
    @classmethod
    def _load_file_from_memory(cls, file) -> io.BytesIO:
        if file.endswith(".json") and cls.memory[file]["extend"]:
            return _extend_json_from_memory(file, cls.memory[file]["file"])
        return io.BytesIO(cls.memory[file]["file"])

    @classmethod
    def load_file(cls, file, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        """Reimplementation of the builtin open function that uses the lookup table to redirect file paths.
        https://docs.python.org/3/library/functions.html#open

        Returns:
            io.TextIOWrapper | io.BytesIO: just treat this like a file you'll be fine
        """
        # if file.endswith(".png"):
        # print(file)
            # pass
        if not isinstance(file, str):
           return Path(file).open(mode, buffering, encoding, errors, newline)
        if file.replace("\\", "/") in cls.memory.keys():
            return cls._load_file_from_memory(file)
        if file.replace("\\", "/") in cls.lookup_table.keys():
            if file.endswith(".json") and cls.lookup_table[file.replace("\\", "/")]["extend"]:
                return _extend_json(cls.lookup_table[file.replace("\\", "/")]["file"], file)
            file = cls.lookup_table[file.replace("\\", "/")]["file"]
        return Path(file.replace("\\", "/")).open(mode, buffering, encoding, errors, newline)

    @classmethod
    def change_binding(cls, original: str, data: str, extend: bool = False) -> None:
        """Changes the binding of a file to a new file, and whether or not it should be merged with the other."""
        original = original.replace("\\", "/")
        cls.lookup_table[original] = {
            "file": data,
            "extend": extend
        }

    @classmethod
    def change_binding_in_memory(cls, original: str, new, mod_name: str, extend: bool = False) -> None:
        """Changes the binding of a file to a new file, and whether or not it should be merged with the other."""
        original = original.replace("\\", "/")
        if original in cls.memory.keys():
            proper_name = '/'.join(original.split("/")[1:])
            print(f'Warning: Both "{cls.memory[original].get("mod")}" and "{mod_name}" are trying to modify {proper_name}. Only the latter will be applied.')
        cls.memory[original] = {
            "file": new,
            "extend": extend,
            "mod": mod_name
        }
    
    @classmethod
    def get_path(cls, file: str) -> str:
        """Gets the path of a file, replacing it with the modded version if it exists."""
        if not cls.enabled: 
            return file
        file = file.replace("\\", "/")
        if file in cls.lookup_table.keys():
            return cls.lookup_table[file]["file"]
        return file

    @classmethod
    def toggle(cls) -> None:
        """Toggles the file loader on and off. When off, the original files are loaded. Clears the cache when disabled."""
        cls.enabled = not cls.enabled
        if not cls.enabled:
            from scripts.ui.image_cache import clear_cache
            clear_cache()
    
    @classmethod
    def clear_memory(cls) -> None:
        """Clears the memory cache of all loaded files."""
        cls.memory = {}
    
    @classmethod
    def clear_lookup_table(cls) -> None:
        """Clears the lookup table of all file bindings."""
        cls.lookup_table = {}

def get_path(file: str) -> str:
    """Gets the path of a file, replacing it with the modded version if it exists."""
    return _FileHandler.get_path(file)

def image_load(file: str) -> pygame.Surface:
    """Replacement for pygame.image.load that will replace files if a mod has changed them.

    Args:
        file (str)

    Returns:
        pygame.Surface
    """
    if file in _FileHandler.memory.keys():
        return pygame.image.load(_FileHandler._load_file_from_memory(file))
    return pygame.image.load(_FileHandler.get_path(file))

builtins.open = _FileHandler.load_file