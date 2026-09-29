from __future__ import annotations

import os
from dataclasses import dataclass, field


class ConfigError(Exception):
    pass


@dataclass
class MQTTConfig:
    broker: str
    port: int = 1883
    username: str = ""
    password: str = ""
    topic: str = "msh/#"
    encryption_key: str = "1PG7OiApB1nwvP+rz05pAQ=="


@dataclass
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8080


@dataclass
class DBConfig:
    path: str = "/data/trace-graph.db"


@dataclass
class ObservabilityConfig:
    enabled: bool = False
    service_name: str = "mesh-graph"
    environment: str = "dev"
    exporter: str = "otlp"
    otlp_endpoint: str = "http://127.0.0.1:4317"
    sample_ratio: float = 1.0


@dataclass
class Config:
    mqtt: MQTTConfig
    api: APIConfig = field(default_factory=APIConfig)
    db: DBConfig = field(default_factory=DBConfig)
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)


def _env(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key, default)


def _require_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise ConfigError(f"Missing required environment variable: {key}")
    return value


def load_config_from_env() -> Config:
    """Load configuration entirely from environment variables.

    Required:
        MQTT__BROKER

    Optional (with defaults):
        MQTT__PORT            (1883)
        MQTT__USERNAME        ("")
        MQTT__PASSWORD        ("")
        MQTT__TOPIC           ("msh/#")
        MQTT__ENCRYPTION_KEY  ("1PG7OiApB1nwvP+rz05pAQ==")
        API__HOST             ("0.0.0.0")
        API__PORT             (8080)
        DB__PATH              ("/data/trace-graph.db")
        OBSERVABILITY__ENABLED         (false)
        OBSERVABILITY__SERVICE_NAME    ("mesh-graph")
        OBSERVABILITY__ENVIRONMENT     ("dev")
        OBSERVABILITY__EXPORTER        ("otlp")
        OBSERVABILITY__OTLP_ENDPOINT   ("http://127.0.0.1:4317")
        OBSERVABILITY__SAMPLE_RATIO    (1.0)
    """
    mqtt = MQTTConfig(
        broker=_require_env("MQTT__BROKER"),
        port=int(_env("MQTT__PORT", "1883")),  # type: ignore[arg-type]
        username=_env("MQTT__USERNAME", "") or "",
        password=_env("MQTT__PASSWORD", "") or "",
        topic=_env("MQTT__TOPIC", "msh/#"),  # type: ignore[arg-type]
        encryption_key=_env("MQTT__ENCRYPTION_KEY", "1PG7OiApB1nwvP+rz05pAQ=="),  # type: ignore[arg-type]
    )
    api = APIConfig(
        host=_env("API__HOST", "0.0.0.0"),  # type: ignore[arg-type]
        port=int(_env("API__PORT", "8080")),  # type: ignore[arg-type]
    )
    db = DBConfig(
        path=_env("DB__PATH", "/data/trace-graph.db"),  # type: ignore[arg-type]
    )
    observability = ObservabilityConfig(
        enabled=_env("OBSERVABILITY__ENABLED", "false").lower() in ("1", "true", "yes"),  # type: ignore[union-attr]
        service_name=_env("OBSERVABILITY__SERVICE_NAME", "mesh-graph"),  # type: ignore[arg-type]
        environment=_env("OBSERVABILITY__ENVIRONMENT", "dev"),  # type: ignore[arg-type]
        exporter=_env("OBSERVABILITY__EXPORTER", "otlp"),  # type: ignore[arg-type]
        otlp_endpoint=_env("OBSERVABILITY__OTLP_ENDPOINT", "http://127.0.0.1:4317"),  # type: ignore[arg-type]
        sample_ratio=float(_env("OBSERVABILITY__SAMPLE_RATIO", "1.0")),  # type: ignore[arg-type]
    )
    return Config(mqtt=mqtt, api=api, db=db, observability=observability)

