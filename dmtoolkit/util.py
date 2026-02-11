"""Random utility stuff."""

import logging

def normalize_name(name: str) -> str:
    """Normalizes a string for use as an ID."""
    separatators = {" ", "\t", "\n", "-", "_", ".", "|"}
    finalstring = ""
    for char in name:
        if char in separatators:
            finalstring += char
        elif char.isalnum():
            finalstring += char.lower()
    return finalstring

def get_logger(name: str):
    """Standardized logger creation for all modules."""
    log = logging.getLogger(name)
    try:
        # Try to infer the logging level from the flask env config value
        from flask import current_app
        if "dev" in current_app.config["FLASK_ENV"]:
            log.setLevel("DEBUG")
        else:
            log.setLevel("INFO")
    except:
        log.setLevel("DEBUG") # Default to debug logging
    return log