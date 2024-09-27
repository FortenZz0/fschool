import json


def _get_content(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()
    
    
def get_settings():
    content = _get_content("./set.json")
    
    return json.loads(content)