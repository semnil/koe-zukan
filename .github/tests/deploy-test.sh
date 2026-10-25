#!/usr/bin/env bash
# Checks the events deploy.yml runs on and what its jobs do on them: pull_request (with no filter), push to master and
# workflow_dispatch start it; the build job has no condition, so `build`, a required status check of master, reports on
# every pull request, and its token can only read the repository; the deploy job runs after the build job and is
# skipped on a pull request; a pull request runs in a concurrency group of its own, apart from the `pages` group of a
# push or a manual run.
# WORKFLOW_FILE selects the workflow under test (relative to the repository root, or absolute).
set -euo pipefail

root=$(cd "$(dirname "$0")/../.." && pwd)
workflow="${WORKFLOW_FILE:-.github/workflows/deploy.yml}"
case "$workflow" in
  /*) workflow_path="$workflow" ;;
  *) workflow_path="$root/$workflow" ;;
esac
count=0
failures=0

# expect <name> <actual> <expected>
expect() {
  count=$((count + 1))
  if [ "$2" = "$3" ]; then
    echo "ok   $1"
  else
    failures=$((failures + 1))
    echo "FAIL $1: expected $3, got $2"
  fi
}

expect 'push, pull_request and workflow_dispatch are the triggers' "$(yq -o=json -I=0 '.on | keys | sort' "$workflow_path")" '["pull_request","push","workflow_dispatch"]'
expect 'the pull_request trigger has no filter' "$(yq -r '.on.pull_request == null' "$workflow_path")" 'true'
expect 'push starts it on master only' "$(yq -o=json -I=0 '.on.push' "$workflow_path")" '{"branches":["master"]}'
expect 'the build job has no condition' "$(yq -r '.jobs.build | has("if")' "$workflow_path")" 'false'
expect 'the build job token can only read the repository' "$(yq -o=json -I=0 '.jobs.build.permissions' "$workflow_path")" '{"contents":"read"}'
expect 'the deploy job runs after the build job' "$(yq -r '.jobs.deploy.needs' "$workflow_path")" 'build'
expect 'the deploy job is skipped on a pull request' "$(yq -r '.jobs.deploy.if' "$workflow_path")" "github.event_name != 'pull_request'"
expect 'a pull request has its own concurrency group' "$(yq -r '.concurrency.group' "$workflow_path")" "\${{ github.event_name == 'pull_request' && format('pages-pr-{0}', github.event.pull_request.number) || 'pages' }}"

echo "${count} checks, ${failures} failed"
[ "$failures" -eq 0 ]
