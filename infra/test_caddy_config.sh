#!/usr/bin/env bash
# Smoke test for infra/Caddyfile (runs in CI before every deploy; needs Docker).
#  1. the config is valid;
#  2. every response has the security headers and NO "Server" header (neither Caddy's nor the upstream's);
#  3. hashed /assets/* files are cached for a year, UI pages are revalidated, /api is not given a UI cache rule.
# Stand-in upstreams: python http.server containers named "frontend" and "backend" (they send their own Server header).
set -euo pipefail
cd "$(dirname "$0")"

IMAGE=caddy:2-alpine
NET="caddy-test-$$"
SITE="$(mktemp -d)"
PORT=18080
cleanup() {
  docker rm -f caddy-test-caddy caddy-test-frontend caddy-test-backend >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
  rm -rf "$SITE"
}
trap cleanup EXIT

echo "== validate"
docker run --rm -v "$PWD/Caddyfile:/etc/caddy/Caddyfile:ro" -e DOMAIN=example.sslip.io "$IMAGE" \
  caddy validate --adapter caddyfile --config /etc/caddy/Caddyfile

echo "== start caddy + stand-in upstreams"
mkdir -p "$SITE/assets" "$SITE/api"
echo '<!doctype html><title>ok</title>' > "$SITE/index.html"
echo 'console.log(1)' > "$SITE/assets/index-abc123.js"
echo '{"status":"ok"}' > "$SITE/api/health"
chmod -R a+rX "$SITE"
docker network create "$NET" >/dev/null
for name in frontend backend; do
  port=$([ "$name" = frontend ] && echo 80 || echo 8000)
  docker run -d --name "caddy-test-$name" --network "$NET" --network-alias "$name" -v "$SITE:/srv:ro" \
    python:3.12-alpine python -m http.server "$port" -d /srv >/dev/null
done
# DOMAIN=:8080 -> plain HTTP on port 8080 (no certificates needed in the test)
docker run -d --name caddy-test-caddy --network "$NET" -p "$PORT:8080" -e DOMAIN=:8080 \
  -v "$PWD/Caddyfile:/etc/caddy/Caddyfile:ro" "$IMAGE" >/dev/null
for _ in $(seq 1 30); do
  curl -fs "http://localhost:$PORT/healthz" >/dev/null 2>&1 && curl -fs "http://localhost:$PORT/" >/dev/null 2>&1 && break
  sleep 1
done

fail=0
check() {  # check <path> <expected cache-control or "-" for none / "*" for any>
  local path="$1" cache="$2" headers
  headers="$(curl -s -D - -o /dev/null "http://localhost:$PORT$path" | tr -d '\r')"
  echo "-- $path"; echo "$headers" | sed 's/^/   /'
  for h in "Strict-Transport-Security: max-age=31536000; includeSubDomains" "X-Content-Type-Options: nosniff" \
           "X-Frame-Options: DENY" "Content-Security-Policy: frame-ancestors 'none'" \
           "Referrer-Policy: strict-origin-when-cross-origin"; do
    echo "$headers" | grep -qiF "$h" || { echo "FAIL $path: missing '$h'"; fail=1; }
  done
  if echo "$headers" | grep -qi '^server:'; then echo "FAIL $path: Server header present"; fail=1; fi
  case "$cache" in
    -) if echo "$headers" | grep -qi '^cache-control: no-cache'; then echo "FAIL $path: UI cache rule on API"; fail=1; fi ;;
    \*) ;;
    *) echo "$headers" | grep -qiF "Cache-Control: $cache" || { echo "FAIL $path: expected Cache-Control '$cache'"; fail=1; } ;;
  esac
}
check /healthz "*"
check / "no-cache"
check /history "no-cache"
check /assets/index-abc123.js "public, max-age=31536000, immutable"
check /api/health "-"

[ "$fail" = 0 ] && echo "== Caddyfile OK" || { echo "== Caddyfile checks FAILED"; docker logs caddy-test-caddy | tail -20; exit 1; }
