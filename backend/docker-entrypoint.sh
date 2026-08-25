set -eu

python - <<'PY'
import os
import socket
import time
import urllib.parse

database_url = os.environ["DATABASE_URL"]
parsed = urllib.parse.urlparse(database_url)
host = parsed.hostname
port = parsed.port or 5432
deadline = time.time() + 60
last_error = None

print(f"Waiting for PostgreSQL at {host}:{port}...", flush=True)

while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print("PostgreSQL is reachable.", flush=True)
            break
    except OSError as exc:
        last_error = exc
        time.sleep(2)
else:
    raise SystemExit(
        f"PostgreSQL unavailable after 60s: {last_error}"
    )
PY

alembic upgrade head
python -m scripts.create_demo_user
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
