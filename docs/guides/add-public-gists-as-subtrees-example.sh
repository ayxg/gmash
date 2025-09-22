#!/bin/bash
_user="your_name_here"
_hashes=(
    "gist_hash_1"
    "gist_hash_2"
    "gist_hash_3"
)

_names=(
    "description_1"
    "description_2"
    "description_3"
)

for i in "${!_hashes[@]}"; do
    _hash="${_hashes[i]}"
    _name="${_names[i]}"
    echo "Hash: $_hash, Name: $_name"
    gmash subtree new -l "https://gist.github.com/$_user/$_hash.git" \
    --path "gist/$_name-$_hash" -b master -B main -R "$_name-$_hash"
    sleep 2
done