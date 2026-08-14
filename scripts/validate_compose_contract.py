from pathlib import Path
import yaml

compose = yaml.safe_load(Path("docker-compose.yml").read_text(encoding="utf-8"))
services = compose["services"]
assert set(services) == {"web", "worker", "redis", "sandbox"}
assert "app_network" in compose["networks"]
assert compose["networks"]["sandbox_internal"]["internal"] is True
assert "sandbox_internal" in services["redis"]["networks"]
assert "app_network" in services["web"]["networks"]
assert "app_network" in services["worker"]["networks"]
assert "ports" not in services["redis"]
assert "ports" not in services["sandbox"]
for service in (services["web"], services["worker"], services["sandbox"]):
    text = str(service)
    assert "change-this-in-production" not in text
print("compose_contract=ok")
