#!/usr/bin/env sh
set -eu

wait_for_tcp() {
  host="$1"
  port="$2"
  name="$3"

  python - "$host" "$port" "$name" <<'PY'
import socket
import sys
import time

host, port, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
deadline = time.time() + 60

while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"{name} is ready")
            raise SystemExit(0)
    except OSError:
        time.sleep(1)

print(f"Timed out waiting for {name} at {host}:{port}", file=sys.stderr)
raise SystemExit(1)
PY
}

wait_for_tcp "${POSTGRES_HOST:-postgres}" "${POSTGRES_PORT:-5432}" "postgres"
wait_for_tcp "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}" "redis"

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  alembic upgrade head
fi

case "${1:-api}" in
  api)
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
    ;;
  worker)
    exec python -m app.worker
    ;;
  *)
    exec "$@"
    ;;
esac
