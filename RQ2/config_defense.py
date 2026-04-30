"""Configuration utilities for ChainBreaker."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class ChainBreakerConfig:
    """Top-level configuration object."""

    sandbox_image: str = "chainbreaker/sandbox:latest"
    mock_server_host: str = "127.0.0.1"
    mock_server_port: int = 8080
    hijack_domains: List[str] = field(
        default_factory=lambda: ["evil.com", "exfil.io", "attacker.cn"]
    )
    max_workers: int = 2
    output_dir: Path = field(default_factory=lambda: Path("outputs"))
    log_level: str = "INFO"
    api_keys: Dict[str, str] = field(default_factory=dict)

    @property
    def mock_server_url(self) -> str:
        return f"http://{self.mock_server_host}:{self.mock_server_port}"

    @classmethod
    def from_env(cls) -> "ChainBreakerConfig":
        """Load configuration from environment variables."""
        defaults = cls()
        cfg = cls(
            sandbox_image=os.getenv("CB_SANDBOX_IMAGE", defaults.sandbox_image),
            mock_server_host=os.getenv("CB_MOCK_HOST", defaults.mock_server_host),
            mock_server_port=int(os.getenv("CB_MOCK_PORT", defaults.mock_server_port)),
            hijack_domains=os.getenv("CB_HIJACK_DOMAINS", ",".join(defaults.hijack_domains)).split(","),
            max_workers=int(os.getenv("CB_MAX_WORKERS", defaults.max_workers)),
            output_dir=Path(os.getenv("CB_OUTPUT_DIR", str(defaults.output_dir))),
            log_level=os.getenv("CB_LOG_LEVEL", defaults.log_level),
        )
        cfg.api_keys = cls._load_api_keys_from_env()
        return cfg

    @staticmethod
    def _load_api_keys_from_env() -> Dict[str, str]:
        keys = {}
        for key in (
            "OPENAI_API_KEY",
            "OPENAI_BASE_URL",
            "OPENAI_MODEL",
            "ANTHROPIC_API_KEY",
            "OPENCLAW_GATEWAY_URL",
            "OPENCLAW_GATEWAY_TOKEN",
            "OPENCLAW_GATEWAY_PASSWORD",
        ):
            val = os.getenv(key)
            if val:
                keys[key] = val
        return keys

    def to_sandbox_env(self) -> Dict[str, str]:
        """Return environment variables to inject into the sandbox container."""
        return dict(self.api_keys)

    @classmethod
    def from_json(cls, path: Path) -> "ChainBreakerConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        if "output_dir" in data:
            data["output_dir"] = Path(data["output_dir"])
        return cls(**data)
