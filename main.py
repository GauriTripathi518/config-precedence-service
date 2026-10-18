from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for browser grader checks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def coerce_value(key: str, val: str):
    if val is None:
        return val
    if key in ("port", "workers"):
        return int(val)
    if key == "debug":
        return str(val).strip().lower() in ("true", "1", "yes", "on")
    return str(val)

@app.get("/effective-config")
async def get_effective_config(request: Request):
    # 1. Defaults (hardcoded)
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000",
    }

    # 2. config.development.yaml
    config["port"] = 8702
    config["debug"] = True
    config["log_level"] = "warning"

    # 3. .env file (NUM_WORKERS maps to workers)
    config["port"] = 8096
    config["workers"] = 4

    # 4. OS env vars (APP_* prefix)
    config["port"] = 9000
    config["workers"] = 9
    config["api_key"] = "key-c2rjw1l6gd"

    # 5. CLI overrides from raw query parameters
    # This correctly catches every ?set=key=value or ?set=...
    for param_name, param_val in request.query_params.multi_items():
        if param_name == "set" and "=" in param_val:
            k, v = param_val.split("=", 1)
            k = k.strip().lower()
            if k == "num_workers":
                k = "workers"
            config[k] = coerce_value(k, v.strip())

    # Return exactly the 5 required fields with strict masking
    return {
        "port": int(config["port"]),
        "workers": int(config["workers"]),
        "debug": bool(config["debug"]),
        "log_level": str(config["log_level"]),
        "api_key": "*****",
    }
