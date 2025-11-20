#!/bin/bash

# SPDX-FileCopyrightText: 2025 GitHub
# SPDX-License-Identifier: MIT

# Script for updating the version number. Call it like this:
#
# ./release_tools/version_bump minor
#
# It uses `hatch version` to update the version number. Use
# major/minor/micro to determine which part of the version number to
# bump. It creates a new branch and commits the version number
# change.
#
# This script does not push the change to GitHub, so you need to do
# that manually.

if [[ $# -eq 0 ]] ; then
    echo 'usage: ./release_tools/version_bump.sh [ARG]'
    echo 'ARG is passed to the hatch version command to bump the version number.'
    echo 'ARG is usually "major", "minor", or "micro".'
    exit 0
fi

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

# Bump version number
if ! hatch version "$@" ; then
    echo "Failed to update version"
    exit 1
fi

NEW_VERSION_NUMBER=$(hatch version)

# Create new branch
if ! git checkout -b "version-$NEW_VERSION_NUMBER" ; then
    echo "Creating the branch failed."
    git restore .
    exit 1
fi

# Commit the version number change.
if ! git commit -a -m "Version $NEW_VERSION_NUMBER" ; then
    echo "git commit failed"
    exit 1
fi

echo
echo "I have updated the version number locally."
echo "The branch is ready for you to push to GitHub and create a pull request."
