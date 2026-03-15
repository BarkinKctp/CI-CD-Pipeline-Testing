#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

: "${DOCKERHUB_USERNAME:?DOCKERHUB_USERNAME is required}"
: "${DOCKERHUB_TOKEN:?DOCKERHUB_TOKEN is required}"
: "${DOCKER_TEST_IMAGE:?DOCKER_TEST_IMAGE is required}"

BUILD_CONTEXT="${BUILD_CONTEXT:-docker/dockerhub-image}"
SHA_IMAGE_TAG="${SHA_IMAGE_TAG:-}"

echo "Logging in to Docker Hub..."
echo "${DOCKERHUB_TOKEN}" | docker login -u "${DOCKERHUB_USERNAME}" --password-stdin

echo "Building image: ${DOCKER_TEST_IMAGE}"
docker build -t "${DOCKER_TEST_IMAGE}" "${BUILD_CONTEXT}"

echo "Pushing image: ${DOCKER_TEST_IMAGE}"
docker push "${DOCKER_TEST_IMAGE}"

if [[ -n "${SHA_IMAGE_TAG}" ]]; then
  echo "Tagging and pushing SHA image: ${SHA_IMAGE_TAG}"
  docker tag "${DOCKER_TEST_IMAGE}" "${SHA_IMAGE_TAG}"
  docker push "${SHA_IMAGE_TAG}"
fi

echo "Docker image push complete."
