#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Configuration
readonly CLONE_TEMP_DIR="${CLONE_TEMP_DIR:-/tmp/target-repo}"
readonly MAX_CLONE_ATTEMPTS="${MAX_CLONE_ATTEMPTS:-3}"
readonly CLONE_RETRY_DELAY="${CLONE_RETRY_DELAY:-2}"

# Logging functions
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $*" >&2
}

log_error() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" >&2
}

log_warning() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $*" >&2
}

# Cleanup function called on exit
cleanup() {
  local exit_code=$?
  
  if [ $exit_code -ne 0 ]; then
    log_error "Container entrypoint failed with exit code $exit_code"
    # Clean up partial clone on failure
    if [ -d "${CLONE_TEMP_DIR}" ]; then
      log "Cleaning up failed clone directory: ${CLONE_TEMP_DIR}"
      rm -rf "${CLONE_TEMP_DIR}" 2>/dev/null || true
    fi
  fi
  
  exit $exit_code
}

# Set trap to run cleanup on exit
trap cleanup EXIT

# Validate required environment variables
log "Validating environment variables..."

if [ -z "${GH_TOKEN:-}" ]; then
  log_error "GH_TOKEN is missing or empty"
  exit 1
fi

if [ -z "${TARGET_REPO:-}" ]; then
  log_error "TARGET_REPO is missing or empty"
  exit 1
fi

log "Environment validation passed"
log "Target repository: ${TARGET_REPO}"
log "Clone destination: ${CLONE_TEMP_DIR}"

# Attempt to clone repository with retry logic
log "Attempting authenticated clone of ${TARGET_REPO}..."

ATTEMPT=1
while [ $ATTEMPT -le $MAX_CLONE_ATTEMPTS ]; do
  # Clean up previous failed attempt
  if [ -d "${CLONE_TEMP_DIR}" ]; then
    log "Removing previous attempt directory"
    rm -rf "${CLONE_TEMP_DIR}" 2>/dev/null || true
  fi
  
  log "Clone attempt $ATTEMPT of $MAX_CLONE_ATTEMPTS..."
  
  if git clone --depth 1 "https://x-access-token:${GH_TOKEN}@github.com/${TARGET_REPO}.git" "${CLONE_TEMP_DIR}"; then
    log "Clone succeeded on attempt $ATTEMPT"
    break
  fi
  
  if [ $ATTEMPT -lt $MAX_CLONE_ATTEMPTS ]; then
    log_warning "Clone failed on attempt $ATTEMPT"
    log "Waiting ${CLONE_RETRY_DELAY}s before retry..."
    sleep "$CLONE_RETRY_DELAY"
  else
    log_error "Clone failed after $MAX_CLONE_ATTEMPTS attempts"
    exit 1
  fi
  
  ATTEMPT=$((ATTEMPT + 1))
done

# Verify clone integrity
log "Verifying clone integrity..."

if [ ! -d "${CLONE_TEMP_DIR}" ]; then
  log_error "Clone directory does not exist: ${CLONE_TEMP_DIR}"
  exit 1
fi

if ! git -C "${CLONE_TEMP_DIR}" rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  log_error "Clone directory is not a valid git repository"
  exit 1
fi

log "Clone verification succeeded"

# Additional verification: check for .git directory
if [ ! -d "${CLONE_TEMP_DIR}/.git" ]; then
  log_warning "Warning: .git directory not found in clone"
  exit 1
fi

log "Container initialization complete"
log "Repository ready at: ${CLONE_TEMP_DIR}"