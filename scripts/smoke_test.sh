#!/usr/bin/env bash
# Checks that the running stack really works end to end.
# Usage: scripts/smoke_test.sh [api_base_url]
# Default goes through Nginx, exactly like a browser would: http://localhost/api
set -euo pipefail
BASE_URL="${1:-http://localhost/api}"

echo "Waiting for $BASE_URL/health ..."
for i in $(seq 1 30); do
  if curl -fsS "$BASE_URL/health" >/dev/null 2>&1; then
    echo "API is up after ${i}s"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "API did not become healthy in time" >&2
    exit 1
  fi
  sleep 2
done

# When going through Nginx, also check the web page itself is served
if [[ "$BASE_URL" == */api ]]; then
  echo "Checking the web page ..."
  curl -fsS "${BASE_URL%/api}/" | grep -q "TaskBoard"
fi

echo "Creating a to-do ..."
curl -fsS -X POST "$BASE_URL/todos" \
  -H 'Content-Type: application/json' \
  -d '{"title":"smoke test"}' | grep -q '"smoke test"'

echo "Listing to-dos ..."
curl -fsS "$BASE_URL/todos" | grep -q '"smoke test"'

echo "SMOKE TEST PASSED"
