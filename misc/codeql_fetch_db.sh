#!/bin/bash

# dep: https://github.com/cli/cli
# e.g. get_codeql_db.sh ntp-project/ntp cpp

# CodeQL languages:
#
# - cpp: The C and C++ programming language
# - csharp: The C# programming language
# - go: The Go programming language
# - java: The Java programming language
# - javascript: The JavaScript programming language (including TypeScript)
# - python: The Python programming language
# - ruby: The Ruby programming language
# - swift: The Swift programming language
# - rust: The Rust programming language

if [[ "$#" -ne 2 ]]; then
    echo "Usage: $0 github/nwo language"
    exit 1
fi

db_info=$(gh api /repos/"$1"/code-scanning/codeql/databases --jq ".[] | select(.language == \"$2\")")

if [[ "$?" -ne 0 ]]; then
    exit 1
fi

if [[ $db_info ]]; then
    dst=$(echo "$1_$2_codeql_db.zip" | sed 's/\//_/g')
    echo "Downloading CodeQL database to $PWD/$dst"
    if [ -e "$dst" ]; then
        echo "$dst already exists!"
        exit 1
    fi
    gh api /repos/"$1"/code-scanning/codeql/databases/"$2" -H 'Accept: application/zip' > "$dst"
    echo "Unzip database before use!"
else
    echo "No $2 database available for $1"
    exit 1
fi
