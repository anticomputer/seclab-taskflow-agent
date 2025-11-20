#!/bin/bash

# SPDX-FileCopyrightText: 2025 GitHub
# SPDX-License-Identifier: MIT

# Create a signed tag for the new version number.  This script is
# intended to be run after you have created a new version number
# (using `version_bump.sh` is recommended) and the change has been
# merged into main.
#
# This script does not push the tag to GitHub, so you need to do
# that manually.

# Check that the main branch is checked out.
if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ] ; then
    echo "Please check out the main branch before running this command."
    exit 1
fi

# Check no uncommitted changes.
git update-index --refresh 
if ! git diff-index --quiet HEAD -- ; then
    echo "There are uncommitted file changes. Aborting."
    exit 1
fi

# Check that this commit is signed by GitHub, to avoid
# accidentally tagging a commit that only exists locally.
if [ $(git verify-commit HEAD --raw 2>&1 | grep -E "GOODSIG [A-F0-9]+ GitHub" -c) -eq 0 ] ; then
    echo "This commit hasn't been signed by GitHub."
    echo "Please check that you are attempting to tag the correct commit."
    exit 1
fi

# Check that this is a merge commit.
if ! git rev-parse HEAD^2 ; then
    echo "This is not a merge commit."
    echo "Please check that you are attempting to tag the correct commit."
    exit 1
fi

PROJECT_NAME=$(hatch project metadata name)
VERSION_NUMBER=$(hatch version)
TAG_NAME="v$VERSION_NUMBER"

# Create tag
if ! git tag $TAG_NAME -s -m "Release $PROJECT_NAME version $VERSION_NUMBER." ; then
    echo "Failed to create the tag"
    exit 1
fi

REMOTE_NAME=$(git for-each-ref --format='%(upstream:remotename)' refs/heads/main)

echo
echo "I have created tag $TAG_NAME. You can push it to GitHub like this:"
echo "git push $REMOTE_NAME tag $TAG_NAME"
