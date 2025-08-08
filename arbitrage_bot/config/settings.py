import os
import yaml
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path


def _strip_inline_comment(value: Optional[str]) -> Optional[str]:
    """
    Return the value without any inline '# ...' comment.
    Example: 'configs/prod.yml  # prod config' -> 'configs/prod.yml'
    """
    if value is None:
        return None
    # Only strip if '#' is present and it's not the first char of the line
    head, sep, _ = value.partition("#")
    return head.strip() if sep else value.strip()


def _project_root() -> Path:
    # settings.py is at: <repo>/arb_bot/config/settings.py  -> go two levels up
    return Path(__file__).resolve().parents[2]

def _resolve_config_path(raw_path: Optional[str]) -> Path:
    """
    Resolve CONFIG_FILE relative to the project root and validate existence.
    Also strip inline comments if the user added them by mistake.
    """
    default_rel = "configs/triangular_example.yml"
    clean = _strip_inline_comment(raw_path) or default_rel
    cfg_path = (_project_root() / clean).resolve()
    if not cfg_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {cfg_path}\n"
            f"Hint: set CONFIG_FILE in .env to an existing YAML "
            f"(e.g., configs/triangular_example.yml)."
        )
    return cfg_path


def _load_env() -> None:
    # load the .env file using dotenv
    load_dotenv()

def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML at {path} must be a mapping (dict) at the top level.")
    return data

def _bool_env(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass 
class Settings:
        # Raw merged config (YAML + env-derived fields)
    yaml: Dict[str, Any]

    # Common toggles
    paper_mode: bool
    log_level: str

    # Selected config path (absolute)
    config_path: Path

    # Exchange keys pulled from env
    api_keys: Dict[str, Dict[str, Optional[str]]]

    @property
    def exchanges(self) -> List[Dict[str, Any]]:
        # Expect something like:
        # exchanges:
        #   - name: binance
        #     symbols: [BTC/USDT, ETH/USDT, ETH/BTC]
        return self.yaml.get("exchanges", [])

    @property
    def strategy(self) -> Optional[str]:
        # Either 'strategy: triangular' or strategies: [...]
        if "strategy" in self.yaml:
            return self.yaml["strategy"]
        strategies = self.yaml.get("strategies")
        if isinstance(strategies, list) and strategies:
            return strategies[0]
        return None

    @property
    def risk(self) -> Dict[str, Any]:
        # e.g., {'max_usd_per_trade': 500, 'max_slippage_pct': 0.05, ...}
        return self.yaml.get("risk", {})

    @property
    def symbols_flat(self) -> List[str]:
        # Convenience: flatten symbols from all exchanges
        out: List[str] = []
        for ex in self.exchanges:
            out.extend(ex.get("symbols", []) or [])
        # dedupe while preserving order
        seen = set()
        deduped = []
        for s in out:
            if s not in seen:
                seen.add(s)
                deduped.append(s)
        return deduped


def build_settings() -> Settings:
    _load_env()

    # Read and sanitize CONFIG_FILE (strip inline comment if any)
    config_file_raw = os.getenv("CONFIG_FILE")
    config_path = _resolve_config_path(config_file_raw)

    yaml_cfg = _load_yaml(config_path)
    

    # Pull env toggles
    paper_mode = _bool_env("PAPER_MODE", default=True)
    log_level = (os.getenv("LOG_LEVEL", "INFO") or "INFO").strip().upper()

    # Collect API keys by convention (uppercased exchange names)
    # Add more exchanges as needed
    api_keys = {}
    exchanges = yaml_cfg["exchanges"]
    for exchange in exchanges:
        exchange_name = exchange["name"].upper()
        api_keys[exchange_name] = {
                "key": os.getenv(f"{exchange_name}_API_KEY"),
                "secret": os.getenv(f"{exchange_name}_SECRET"),
        }


    settings = Settings(
        yaml=yaml_cfg,
        paper_mode=paper_mode,
        log_level=log_level,
        config_path=config_path,
        api_keys=api_keys,
    )
    return settings



settings = build_settings()
print(settings)





