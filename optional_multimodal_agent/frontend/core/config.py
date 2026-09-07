from shared.config import env
BACKEND_URL = env("BACKEND_URL","http://127.0.0.1:8000").rstrip("/")
