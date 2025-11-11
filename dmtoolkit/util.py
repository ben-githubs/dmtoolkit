"""Random utility stuff."""

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