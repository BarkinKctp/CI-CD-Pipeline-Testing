#!/usr/bin/env bash
set -euo pipefail

echo "Container started."

if [ -z "${GH_TOKEN:-}" ]; then
  echo "GH_TOKEN is missing."
  exit 1
fi

if [ -z "${TARGET_REPO:-}" ]; then
  echo "TARGET_REPO is missing."
  exit 1
fi

echo "Attempting authenticated clone from inside container..."
git clone "https://x-access-token:${GH_TOKEN}@github.com/${TARGET_REPO}.git" /tmp/target-repo

if [ ! -d /tmp/target-repo/.git ]; then
  echo "Clone failed."
  exit 1
fi

echo "Authenticated clone succeeded inside container."