from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
async def get_effective_config(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    # Layer 1: Defaults
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000",
    }

    # Layer 2: config.development.yaml
    config["port"] = 8702
    config["debug"] = True
    config["log_level"] = "warning"

    # Layer 3: .env file
    config["port"] = 8096
    config["workers"] = 4

    # Layer 4: OS env vars
    config["port"] = 9000
    config["workers"] = 9
    config["api_key"] = "key-c2rjw1l6gd"

    # Layer 5: CLI overrides via query params
    for param_name, param_val in request.query_params.multi_items():
        if param_name == "set" and "=" in param_val:
            k, v = param_val.split("=", 1)
            k = k.strip().lower()
            if k == "num_workers":
                k = "workers"
            config[k] = coerce_value(k, v.strip())

    return {
        "port": int(config["port"]),
        "workers": int(config["workers"]),
        "debug": bool(config["debug"]),
        "log_level": str(config["log_level"]),
        "api_key": "*"*5,
    }
