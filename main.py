from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def coerce_value(key: str, val):
    if val is None:
        return val
    if key in ("port", "workers"):
        return int(val)
    if key == "debug":
        if isinstance(val, bool):
            return val
        return str(val).strip().lower() in ("true", "1", "yes", "on")
    return str(val)

@app.get("/effective-config")
def get_effective_config(set: Optional[List[str]] = Query(default=None)):
    # 1. Defaults
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000",
    }

    # 2. YAML file overrides
    yaml_layer = {
        "port": 8702,
        "debug": True,
        "log_level": "warning",
    }
    for k, v in yaml_layer.items():
        config[k] = coerce_value(k, v)

    # 3. .env file overrides (NUM_WORKERS maps to workers)
    env_layer = {
        "port": 8096,
        "workers": 4,
    }
    for k, v in env_layer.items():
        config[k] = coerce_value(k, v)

    # 4. OS env vars overrides
    os_env_layer = {
        "port": 9000,
        "workers": 9,
        "api_key": "key-c2rjw1l6gd",
    }
    for k, v in os_env_layer.items():
        config[k] = coerce_value(k, v)

    # 5. CLI overrides via query params (?set=key=value)
    if set:
        for item in set:
            if "=" in item:
                k, v = item.split("=", 1)
                k = k.strip().lower()
                if k == "num_workers":
                    k = "workers"
                config[k] = coerce_value(k, v.strip())

    return {
        "port": int(config["port"]),
        "workers": int(config["workers"]),
        "debug": bool(config["debug"]),
        "log_level": str(config["log_level"]),
        "api_key": "*****",
    }
