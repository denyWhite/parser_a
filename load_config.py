import tomllib
from pathlib import Path

import tomli_w

from dto import AvitoConfig

_BASE_DIR = Path(__file__).parent
_LOCAL_CONFIG = _BASE_DIR / "local_config.toml"
_DEFAULT_CONFIG = _BASE_DIR / "config.toml"


def _resolve_config_path(path: str) -> Path:
    if path == "config.toml" and _LOCAL_CONFIG.exists():
        return _LOCAL_CONFIG
    return Path(path)


def load_avito_config(path: str = "config.toml") -> AvitoConfig:
    resolved = _resolve_config_path(path)
    with open(resolved, "rb") as f:
        data = tomllib.load(f)
    return AvitoConfig(**data["avito"])


def save_avito_config(config: dict):
    with _LOCAL_CONFIG.open("wb") as f:
        tomli_w.dump(config, f)
