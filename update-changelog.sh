#!/bin/bash
set -e
NEW_VERSION=$1

$EDITOR HISTORY.md || (c=$?; echo "Failed to edit HISTORY.md"; $(exit $c))

grep -q $NEW_VERSION HISTORY.md || (c=$?; echo "New version $NEW_VERSION is not found in HISTORY.md"; $(exit $c))
