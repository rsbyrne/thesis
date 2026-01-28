#!/bin/bash

currentDir=$PWD
cd "$(dirname "$0")" || exit

QUIET=0
FORCED=0
EXECUTE=0
VERBOSE=0
SYNCHRONISE=0

while getopts "sfevq" flag
do
    case "${flag}" in
        s) SYNCHRONISE=1;;
        q) QUIET=1;;
        f) FORCED=1;;
        e) EXECUTE=1;;
        v) VERBOSE=1;;
    esac
done

if [[ $SYNCHRONISE -eq 1 ]]; then
    echo "Syncing Notebooks to MyST Markdown..."
    # Find all notebooks in book/content
    # --to myst: ensures the target is MyST
    # --update: ONLY updates the .md if the .ipynb is newer
    find content -name ".ipynb_checkpoints" -prune -o -type f -name "*.ipynb" \
     -exec jupytext --sync --to myst {} +
    echo "Sync complete. Ready to build MyST doc."
fi

if [[ $FORCED -eq 1 ]]; then
    echo "🧹 Cleaning build directory..."
    rm -rf _build
fi

cmd="myst build --pdf"

if [[ $EXECUTE -eq 1 ]]; then
    cmd="$cmd --execute"
fi

if [[ $VERBOSE -eq 1 ]]; then
    cmd="$cmd --debug"
fi

if [[ $QUIET -eq 1 ]]; then
    $cmd >/dev/null 2>&1
else
    $cmd
fi

cd "$currentDir" || exit