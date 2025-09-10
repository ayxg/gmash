#!/bin/bash
#@doc##########################################################################
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
###############################################################################
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
###############################################################################
# @file gmash->find command group
# @created: 2025/08/31
#@enddoc#######################################################################

# @brief Uses 'simian' java lib to detect duplicate C++ code in a directory tree.
gmash_find_duplicate_code(){
  local _path=${ARGV_PATH:-$1}
  local _threshold=${ARGV_THRESHOLD:-$2}
  local _cpp_extensions="./*.h ./*.cpp ./*.hpp"
  local _path_changed=""

  if [ -z "$_threshold" ]; then
    vecho_info "Defaulting --threshold to 10"
    _threshold=10
  fi

  if [ -n "$_path" ]; then
    cd "$_path" || exit
    _path_changed=1
  else
    vecho_info "Defaulting --path to current."
    _path="$(pwd)"
  fi

  vecho_info "Input Arguments:"
  vecho "     --path: $_path"
  vecho "     --threshold: $_threshold"
  vecho "      Targeting source files: $_cpp_extensions"
  java -jar /c/lib/simian-4.0.0/simian-4.0.0.jar "$_cpp_extensions" \
   -threshold="$_threshold" -formatter=plain -language=cpp

  if [ -n "$_path_changed" ]; then
    cd - || exit
    vecho_done "Scan complete. Returning to original path."
  else
    vecho_done "Scan complete."
  fi

  return 0;
}

# @output for each found repo : "$repo_dir : $repo_name : [$last_commit]"
gmash_find_gits(){
  if [ $# == 0 ]; then
    local _path=${GMASH_FIND_GITS_PATH:-"$(pwd)"}
  else
    local _path=${1:-"$(pwd)"}
  fi

  vecho_func "gmash->find->gits"
  vecho_info "Input Arguments:
        --path : $_path"
  vecho_process "Searching..."

  if [ -n "$_path" ]; then
    cd "$_path" || return 1
  fi

  find "$_path" -type d -name ".git" | while read -r gitdir; do
    repo_dir="$(dirname "$gitdir")"
    repo_name="$(basename "$repo_dir")"
    cd "$repo_dir" || return 1
    last_commit=$(git log -1 --pretty=format:"%h %ad" --date=short 2>/dev/null)
    echo "$repo_dir : $repo_name : [$last_commit]"
    cd - >/dev/null || return 1
  done

  if [ -n "$_path" ]; then
    cd - || return 1
  fi

  vecho_done "Success."
  return 0
}

# @output for each found file : "$file_path"
gmash_find_sources(){
  if [ $# == 0 ]; then
    local _path=${GMASH_FIND_SOURCES_PATH:-"$(pwd)"}
    local _tgtpath=${GMASH_FIND_SOURCES_TGTPATH:-''}
  else
    local _path=${1:-"$(pwd)"}
    local _tgtpath=${2:-''}
  fi

  vecho_func "gmash->find->sources"
  vecho_info "Input Arguments:
        --path : $_path
        --tgt-path : $_tgtpath"
  vecho_process "Searching..."

  if [ ! -d "$_path" ]; then
    echo_error "Source directory does not exist: $_path"
    return 1
  fi

  files_found_=$(find "$_path" -type f)
  echo "$files_found_"

  if [ -z "$files_found_" ]; then
    echo_error "No files found in $_path."
    return 0
  fi

  vecho_process "Merging found files to target path."

  if [ -n "$_tgtpath" ]; then
    mkdir -p "$_tgtpath"

    find "$_path" -type f | while read src_; do
      relpath_="${src_#"$_path"/}"
      newname_="${relpath_//\\//}"
      newname_="${newname_//\//_}"
      cp -p "$src_" "$_tgtpath/$newname_"
      vecho_action "'$src_' -> '$_tgtpath/$newname_'"
    done
  fi

  vecho_done "Success."
  return 0
}
