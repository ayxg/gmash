#!/bin/bash
#@doc---------------------------------------------------------------------------------------------#
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
#-------------------------------------------------------------------------------------------------#
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
#-------------------------------------------------------------------------------------------------#
# @file GMash documentation generator script.
# @created: 2025/09/21
# @brief
#@enddoc------------------------------------------------------------------------------------------#

readonly GMASH_DOCS_BIN="$GMASH_SOURCE/../docs"
echo -e "\e[31;1m  ⚙  Generating gmash documentation. Path : $GMASH_DOCS_BIN \e[0m"
cd "$GMASH_DOCS_BIN" || exit 1

# $1 = file to add front matter to.
# $2 = nav order
# $3 = parent
add_front_matter(){
    local _file=${1:-""}
    if [ -z "$_file" ] || [ ! -f "$_file" ]; then
        echo "[gmash][gmash-docs.sh][add_front_matter] File '$_file' not found."
        return 1
    fi

    local _nav_order=${2:-999}
    local _parent=${3:-""}
    local _temp_file="${_file}.tmp.$$"

    # Extract title more robustly
    local _title_
    _title_=$(grep -m1 '^# ' "$_file" | sed 's/^# //' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # If no title found, use filename as fallback
    if [ -z "$_title_" ]; then
        _title_=$(basename "$_file" .md)
    fi

    {
        echo "---"
        echo "title: \"$_title_\""
        echo "nav_order: $_nav_order"
        if [ -n "$_parent" ]; then
            echo "parent: \"$_parent\""
        fi
        echo "---"
        echo ""
        cat "$_file"
    } > "$_temp_file" && mv "$_temp_file" "$_file"
}

# $1 = command to call -h on
# $2 = nav order
# $3 = parent
generate_doc_page(){
    local _cmd=${1:-""}
    if [ -z "$_cmd" ]; then
        echo "[gmash][gmash-docs.sh][generate_doc_page] No command provided"
        return 1
    fi
    local _nav_order=${2:-999}
    local _file="cmd-${_cmd// /-}.md" # Replace spaces with dashes
    local _parent=${3:-""}

    echo "[helptext] $_cmd -h | helptext -o $_file"
    $_cmd -h | helptext -o "$_file"
    add_front_matter "$_file" "$_nav_order" "$_parent"
}

# Main
echo "[helptext] gmash -h | helptext -o cmd-gmash.md --skip 3"
gmash -h | helptext -o "cmd-gmash.md" --skip 3
add_front_matter "cmd-gmash.md" "100"

# dirs
generate_doc_page "gmash dirs" "200" "gmash"
    generate_doc_page "gmash dirs prefix" "201" "gmash dirs"
    generate_doc_page "gmash dirs same" "202" "gmash dirs"
    generate_doc_page "gmash dirs separate" "203" "gmash dirs"
    generate_doc_page "gmash dirs squash" "204" "gmash dirs"

# find
generate_doc_page "gmash find" "300" "gmash"
#   generate_doc_page "gmash find duplicate-code" "8" "find"
    generate_doc_page "gmash find gits" "301" "gmash find"
    generate_doc_page "gmash find sources" "302" "gmash find"

# gist
generate_doc_page "gmash gist" "400" "gmash"
    generate_doc_page "gmash gist clone" "401" "gmash gist"
    generate_doc_page "gmash gist create" "402" "gmash gist"
    generate_doc_page "gmash gist prepare" "403" "gmash gist"
    generate_doc_page "gmash gist recover" "405" "gmash gist"
    generate_doc_page "gmash gist upload" "406" "gmash gist"
# lineage
generate_doc_page "gmash lineage" "500" "gmash"
    generate_doc_page "gmash lineage merge" "501" "gmash lineage"

# subtree
generate_doc_page "gmash subtree" "600" "gmash"
    generate_doc_page "gmash subtree new" "601" "gmash subtree"
    generate_doc_page "gmash subtree patch" "602" "gmash subtree"

# mono
generate_doc_page "gmash mono" "700" "gmash"
    generate_doc_page "gmash mono patch" "701" "gmash mono"

echo "Documentation generation complete."