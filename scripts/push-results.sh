#!/usr/bin/env bash
set -euo pipefail

: "${MAIN_TEST_OUTCOME:=failure}"
: "${DOCKER_TEST_OUTCOME:=failure}"

mkdir -p results
STATUS=$([[ "${MAIN_TEST_OUTCOME}" == "success" ]] && [[ "${DOCKER_TEST_OUTCOME}" == "success" ]] && echo "success" || echo "failure")
RESULT_FILE="results/test-flask-${GITHUB_RUN_ID}.md"
printf "# Test Flask Workflow Result\n\n- Status: %s\n- Repository: %s\n- Branch/Ref: %s\n- Run ID: %s\n- Run Number: %s\n- Workflow: %s\n" \
"$STATUS" "$GITHUB_REPOSITORY" "$GITHUB_REF" "$GITHUB_RUN_ID" "$GITHUB_RUN_NUMBER" "$GITHUB_WORKFLOW" > "$RESULT_FILE"
echo "Wrote test result to $RESULT_FILE"

if [ "${GITHUB_EVENT_NAME}" = "pull_request" ]; then
    echo "Pull request event detected. Skipping push to target repo."
    exit 0
fi

if [ ! -f "$RESULT_FILE" ]; then
    echo "Result file not found: $RESULT_FILE"
    exit 1
fi

WORKDIR="$(mktemp -d)"
git clone "https://x-access-token:${GH_TOKEN}@github.com/${TARGET_REPO}.git" "$WORKDIR/target"

mkdir -p "$WORKDIR/target/results"
cp "$RESULT_FILE" "$WORKDIR/target/$RESULT_FILE"

cd "$WORKDIR/target"
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git checkout "$TARGET_BRANCH"
git add "$RESULT_FILE"

if git diff --cached --quiet; then
    echo "No result changes to push."
    exit 0
fi

git commit -m "Add test result for run ${GITHUB_RUN_ID}"
git push origin "$TARGET_BRANCH"
echo "Pushed $RESULT_FILE to ${TARGET_REPO}:${TARGET_BRANCH}"
