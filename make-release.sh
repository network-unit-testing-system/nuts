#!/bin/bash
if [[ $# != 1 ]] ; then
    echo "error: please provide a version tag in the form 'v1.0.0'" >&2
    exit 1
fi

FILE=release_notes/$1.md
if [[ ! -f "$FILE" ]]; then
    echo "$FILE does not exist, please create it first." >&2
    exit 1
fi

git add release_notes/$1.md
git commit -am "add changelog for upcoming release $1"
git push
git tag -a $1 -m "Version $1"
git push origin --tags

