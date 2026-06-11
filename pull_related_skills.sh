#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

REMOTE_NAME="${REMOTE_NAME:-origin}"
BRANCH_NAME="${BRANCH_NAME:-}"
FAILED=0

pull_or_clone() {
  local name="$1"
  local url="$2"
  local path="${SKILLS_ROOT}/${name}"

  if [[ ! -d "${path}/.git" ]]; then
    echo "==> clone ${name}"
    git clone "${url}" "${path}"
    return
  fi

  echo "==> pull ${name}"
  git -C "${path}" remote get-url "${REMOTE_NAME}" >/dev/null

  if [[ -n "$(git -C "${path}" status --porcelain)" ]]; then
    echo "skip ${name}: working tree is not clean" >&2
    return 0
  fi

  if [[ -n "${BRANCH_NAME}" ]]; then
    git -C "${path}" pull --ff-only "${REMOTE_NAME}" "${BRANCH_NAME}"
  else
    git -C "${path}" pull --ff-only "${REMOTE_NAME}"
  fi
}

run() {
  pull_or_clone "$@" || FAILED=1
}

run "python-poetry" "https://github.com/MigoXV/python-poetry.git"
run "protos" "https://github.com/MigoXV/protos.git"
run "dl-train" "https://github.com/MigoXV/dl-train.git"

exit "${FAILED}"
