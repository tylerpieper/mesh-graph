import pytest

from mesh_graph.config import ConfigError, load_config_from_env


def test_valid_full_config(monkeypatch):
    monkeypatch.setenv("MQTT__BROKER", "mqtt.example.com")
    monkeypatch.setenv("MQTT__PORT", "1884")
    monkeypatch.setenv("MQTT__USERNAME", "user")
    monkeypatch.setenv("MQTT__PASSWORD", "pass")
    monkeypatch.setenv("MQTT__TOPIC", "msh/+/2/e/")
    monkeypatch.setenv("MQTT__ENCRYPTION_KEY", "1PG7OiApB1nwvP+rz05pAQ==")
    monkeypatch.setenv("API__HOST", "127.0.0.1")
    monkeypatch.setenv("API__PORT", "9090")
    monkeypatch.setenv("DB__PATH", "/tmp/test.db")
    monkeypatch.setenv("OBSERVABILITY__ENABLED", "true")
    monkeypatch.setenv("OBSERVABILITY__SERVICE_NAME", "mesh-graph-test")
    monkeypatch.setenv("OBSERVABILITY__ENVIRONMENT", "ci")
    monkeypatch.setenv("OBSERVABILITY__EXPORTER", "console")
    monkeypatch.setenv("OBSERVABILITY__OTLP_ENDPOINT", "http://collector:4317")
    monkeypatch.setenv("OBSERVABILITY__SAMPLE_RATIO", "0.25")

    cfg = load_config_from_env()
    assert cfg.mqtt.broker == "mqtt.example.com"
    assert cfg.mqtt.port == 1884
    assert cfg.mqtt.username == "user"
    assert cfg.mqtt.password == "pass"
    assert cfg.mqtt.topic == "msh/+/2/e/"
    assert cfg.mqtt.encryption_key == "1PG7OiApB1nwvP+rz05pAQ=="
    assert cfg.api.host == "127.0.0.1"
    assert cfg.api.port == 9090
    assert cfg.db.path == "/tmp/test.db"
    assert cfg.observability.enabled is True
    assert cfg.observability.service_name == "mesh-graph-test"
    assert cfg.observability.environment == "ci"
    assert cfg.observability.exporter == "console"
    assert cfg.observability.otlp_endpoint == "http://collector:4317"
    assert cfg.observability.sample_ratio == 0.25


def test_defaults_applied(monkeypatch):
    monkeypatch.setenv("MQTT__BROKER", "mqtt.example.com")
    # Clear any env vars that might be set in the test environment
    for key in [
        "MQTT__PORT", "MQTT__USERNAME", "MQTT__PASSWORD", "MQTT__TOPIC", "MQTT__ENCRYPTION_KEY",
        "API__HOST", "API__PORT", "DB__PATH",
        "OBSERVABILITY__ENABLED", "OBSERVABILITY__SERVICE_NAME", "OBSERVABILITY__ENVIRONMENT",
        "OBSERVABILITY__EXPORTER", "OBSERVABILITY__OTLP_ENDPOINT", "OBSERVABILITY__SAMPLE_RATIO",
    ]:
        monkeypatch.delenv(key, raising=False)

    cfg = load_config_from_env()
    assert cfg.mqtt.port == 1883
    assert cfg.mqtt.username == ""
    assert cfg.mqtt.password == ""
    assert cfg.mqtt.topic == "msh/#"
    assert cfg.api.host == "0.0.0.0"
    assert cfg.api.port == 8080
    assert cfg.db.path == "/data/trace-graph.db"
    assert cfg.observability.enabled is False
    assert cfg.observability.service_name == "mesh-graph"
    assert cfg.observability.environment == "dev"
    assert cfg.observability.exporter == "otlp"
    assert cfg.observability.otlp_endpoint == "http://127.0.0.1:4317"
    assert cfg.observability.sample_ratio == 1.0


def test_missing_broker_raises(monkeypatch):
    monkeypatch.delenv("MQTT__BROKER", raising=False)
    with pytest.raises(ConfigError, match="MQTT__BROKER"):
        load_config_from_env()


@pytest.mark.parametrize("enabled_val,expected", [
    ("true", True),
    ("True", True),
    ("TRUE", True),
    ("1", True),
    ("yes", True),
    ("false", False),
    ("0", False),
    ("no", False),
    ("", False),
])
def test_observability_enabled_parsing(monkeypatch, enabled_val, expected):
    monkeypatch.setenv("MQTT__BROKER", "mqtt.example.com")
    monkeypatch.setenv("OBSERVABILITY__ENABLED", enabled_val)
    cfg = load_config_from_env()
    assert cfg.observability.enabled is expected
