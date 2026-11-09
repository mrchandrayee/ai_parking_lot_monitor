from pathlib import Path
import yaml

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg.setdefault("video", {})
    cfg.setdefault("detector", {})
    cfg.setdefault("tracking", {})
    cfg.setdefault("parking", {})
    return cfg

def resolve_source(source):
    if isinstance(source, str) and source.isdigit():
        return int(source)
    return source
