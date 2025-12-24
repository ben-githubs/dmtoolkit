import json
from typing import Any, Optional

from flask import request, Response, make_response

settings_blacklist = [
    "csrf_token",
    "submit"
]

def get_setting(key: str) -> Any:
    return get_settings().get(key)


def get_settings() -> dict:
    return sanitize_settings(json.loads(request.cookies.get("settings", "{}")))


def set_settings(new_settings: dict[str, Any], resp: Optional[Response] = None) -> Response:
    settings = get_settings()
    settings |= new_settings
    if not resp:
        resp = make_response()
    resp.set_cookie("settings", json.dumps(sanitize_settings(settings)))
    return resp


def sanitize_settings(settings: dict[str, Any]) -> dict[str, Any]:
    for field in settings_blacklist:
        settings.pop(field, None)
    return settings

def get_active_modules() -> list[str]:
    """Returns the name of all active modules."""
    active_modules: list[str] = []
    for key, val in get_settings().items():
        if key.startswith("module_") and val:
            active_modules.append(key[7:])
    return active_modules