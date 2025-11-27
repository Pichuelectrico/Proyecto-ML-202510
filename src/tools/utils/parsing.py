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
