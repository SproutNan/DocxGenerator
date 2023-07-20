import base64

def to_base64(bytes):
    return base64.b64encode(bytes).decode("utf-8")

def from_base64(str):
    return base64.b64decode(str)