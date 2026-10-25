#!/usr/bin/env bash
# ==============================================================================
# WindWatch Production Container Deployment Script
# Usage: ./scripts/deploy.sh <target-docker-image>
# Example: ./scripts/deploy.sh tanw9/windwatch:latest
# ==============================================================================
set -euo pipefail

TARGET_IMAGE="${1:-${TARGET_IMAGE:-}}"
if [ -z "$TARGET_IMAGE" ]; then
  echo "ERROR: Target image argument is required."
  echo "Usage: $0 <target-docker-image>"
  exit 1
fi

DATA_DIR="${HOME}/windwatch/data"
mkdir -p "$DATA_DIR"
chmod 775 "$DATA_DIR" 2>/dev/null || true

echo "==> Pulling immutable production image: ${TARGET_IMAGE}..."
docker pull "${TARGET_IMAGE}"

# Clean stale previous backup if exists
docker rm -f windwatch_previous 2>/dev/null || true

# Retain current running container for automated rollback if startup fails
if docker ps -q --filter "name=^/windwatch$" | grep -q .; then
  echo "==> Backing up current running container for safe rollback..."
  docker rename windwatch windwatch_previous 2>/dev/null || true
  docker stop windwatch_previous 2>/dev/null || true
elif docker ps -a -q --filter "name=^/windwatch$" | grep -q .; then
  docker rm -f windwatch 2>/dev/null || true
fi

echo "==> Starting new windwatch container (${TARGET_IMAGE})..."
docker run -d \
  --name windwatch \
  --restart unless-stopped \
  -p 80:8000 \
  -p 8000:8000 \
  -v "${DATA_DIR}:/app/data" \
  "${TARGET_IMAGE}"

echo "==> Validating container health status..."
HEALTHY=0
if command -v curl >/dev/null 2>&1; then
  for i in $(seq 1 15); do
    if curl -sf http://127.0.0.1:8000/api/v1/health > /dev/null; then
      echo "==> Container health check passed!"
      HEALTHY=1
      break
    fi
    echo "Waiting for container warmup ($i/15)..."
    sleep 2
  done
else
  echo "curl not found on host; checking docker inspect status..."
  sleep 5
  if [ "$(docker inspect -f '{{.State.Running}}' windwatch)" = "true" ]; then
    HEALTHY=1
  fi
fi

if [ "$HEALTHY" -ne 1 ]; then
  echo "ERROR: Health check failed! Rolling back to previous running version..."
  docker logs --tail 50 windwatch 2>&1 || true
  docker rm -f windwatch 2>/dev/null || true
  if docker ps -a -q --filter "name=^/windwatch_previous$" | grep -q .; then
    echo "Restoring previous running container..."
    docker start windwatch_previous 2>/dev/null || true
    docker rename windwatch_previous windwatch 2>/dev/null || true
    echo "Rollback completed successfully."
  fi
  exit 1
fi

# Cleanup previous container backup on verified success
docker rm -f windwatch_previous 2>/dev/null || true

# Prune unused images older than 7 days to conserve disk space
docker image prune -af --filter "until=168h" 2>/dev/null || true

echo "==> Deployment successful. Active container:"
docker ps --filter "name=windwatch"
