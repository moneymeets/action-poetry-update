def parse_bool(value: str) -> bool:
    return value.lower() in ["true", "t", "1"]
