import os
import re
from typing import Any, Callable, Mapping, TypeVar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

_SINGLE_TO_PLURAL = {
    "foot": "feet"
}
_PLURAL_TO_SINGLE = {v: k for k, v in _SINGLE_TO_PLURAL.items()}

_DRIVER = None

T = TypeVar("T")

def browser_fetch(url: str) -> str:
    get_driver().get("view-source:" + url)
    import time
    time.sleep(0)
    data = get_driver().find_element(By.TAG_NAME, "pre").text
    return data

def get_driver():
    """Lazily load the browser driver"""
    global _DRIVER
    if not _DRIVER:
        opts = Options()
        opts.headless = True
        os.environ["MOZ_HEADLESS"] = "1"
        _DRIVER = webdriver.Firefox(options=opts)
    return _DRIVER

def pluralize(s: str) -> str:
    """Returns the pluralized version of s, if we know it."""
    if result := _SINGLE_TO_PLURAL.get(s):
        return result
    if s.endswith("s"):
        return s + "es"
    return s + "s"

def singularize(s: str) -> str:
    """Does the reverse of pluralize()."""
    if result := _PLURAL_TO_SINGLE.get(s):
        return result
    if s.endswith("s"):
        return s[:-1]
    return s

class ConverterError(BaseException):
    pass

def deep_get(obj: Mapping, *fields, default: Any = None) -> Any:
    _obj = obj
    for field in fields[:-1]:
        _obj = _obj.get(field, {})
    return _obj.get(fields[-1], default)

def deep_replace(obj: T, pattern: re.Pattern, replace: str|Callable) -> T:
    if isinstance(obj, list):
        return [deep_replace(item, pattern, replace) for item in obj]
    if isinstance(obj, dict):
        return {k: deep_replace(v, pattern, replace) for k, v in obj.items()}
    if isinstance(obj, str):
        return pattern.sub(replace, obj)
    return obj

def regex_flags(flagstr: str) -> re.RegexFlag:
    mapping = {
        "a": re.ASCII,
        "i": re.IGNORECASE,
        "m": re.MULTILINE,
        "s": re.DOTALL,
        "x": re.VERBOSE
    }
    flag = re.UNICODE
    for f in flagstr:
        if m := mapping.get(f.lower()):
            flag &= m
    
    return flag