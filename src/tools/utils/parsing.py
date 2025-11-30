import re
import unicodedata

def parse_content_disposition(value: str):
    if not value:
        return "", {}

    parts = [p.strip() for p in value.split(";") if p.strip()]
    main = parts[0].lower()
    params = {}

    for part in parts[1:]:
        if "=" in part:
            k, v = part.split("=", 1)
            params[k.strip().lower()] = v.strip().strip('"')

    return main, params

def normalize_feature_name(name: str) -> str:
    if not name:
        return ""
    name = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('ASCII')
    name = name.replace("/", "_sobre_")
    name = name.replace("%", "_porcentaje")
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '_', name)
    name = name.strip('_')
    
    return name
