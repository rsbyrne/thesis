#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"/main || exit

export JUPYTER_BASE_URL="http://localhost:8888"
# export JUPYTER_TOKEN="c75d767596e2086ba66caa30a1c2a99ab6e6b74bc73b0272"

export JUPYTER_RUNTIME_DIR="${HOME}/.local/share/jupyter/runtime"
export JUPYTER_TOKEN="$(cat ${JUPYTER_RUNTIME_DIR}/jpserver-7.json | jq -r '.token')"
export JUPYTER_COOKIE_NAME="$(cat ${JUPYTER_RUNTIME_DIR}/jpserver-7.json | jq -r '.cookie_name')"
export JUPYTER_XSRF_TOKEN="$(cat ${JUPYTER_RUNTIME_DIR}/jpserver-7.json | jq -r '.xsrf_token')"

SILENT=0
FORCED=0
EXECUTE=0

while getopts "sfe" flag
do
    case "${flag}" in
        s) SILENT=1;;
        f) FORCED=1;;
        e) EXECUTE=1;;
    esac
done

if [[ $FORCED -eq 1 ]]; then
    rm -rf _build
fi

cmd="myst build --pdf"
if [[ $EXECUTE -eq 1 ]]; then
    cmd="$cmd --execute"
fi

if [[ $SILENT -eq 1 ]]; then
    $cmd >/dev/null 2>&1
else
    $cmd
fi

cd "$currentDir" || exit