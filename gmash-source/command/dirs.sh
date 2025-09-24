#!/bin/bash
#@doc##########################################################################
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
###############################################################################
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
###############################################################################
# @file gmash->dirs command group
# @created: 2025/08/31
#@enddoc#######################################################################

gmash_dirs_prefix(){
  if [ $# == 0 ]; then
    local _prefix="${GMASH_DIRS_PREFIX_PREFIX:-}"
    local _path="${GMASH_DIRS_PREFIX_PATH:-$(pwd)}"
  else
    local _prefix="${1:-''}"
    local _path="${2:-$(pwd)}"
  fi

  vecho_func "gmash->dirs->prefix"

  if [ -z "$_prefix" ]; then
    echo_err "--prefix argument is required."
    return 1
  fi

  if [ -z "$_path" ]; then
    _path="$(pwd)"
  fi

  if [ ! -d "$_path" ] && [ ! -f "$_path" ]; then
    echo_err "Target path '$_path' does not exist."
    return 1
  fi

  vecho_info "Input Arguments:"
  vecho "     --prefix: $_prefix"
  vecho "     --path: $_path"
  vecho_process "Renaming files."

  if [ -f "$_path" ]; then
    basename_="$(basename "$_path")"
    mv "$_path" "$(dirname "$_path")/$_prefix$basename_"
    vecho_action "'$_path' -> '$(dirname "$_path")/$_prefix$basename_'"
    return 0
  else
    for _fp in "$_path"/*; do
      if [ -f "$_fp" ]; then
        basename_="$(basename "$_fp")"
        vecho_action "'$_fp' -> '$_path/$_prefix$basename_'"
        mv "$_fp" "$_path/$_prefix$basename_"
      fi
    done
  fi

  vecho_done "Success."
  return 0
}

gmash_dirs_same(){
  if [ $# == 0 ]; then
    local _path1="${GMASH_DIRS_SAME_PATH:-$(pwd)}"
    local _path2="${GMASH_DIRS_SAME_TGTPATH:-""}"
  else
    local _path1="${1:-$(pwd)}"
    local _path2="${2:-""}"
  fi

  vecho_func "gmash->dirs->same"
  vecho_info "Input Arguments:"
  vecho "     --path: $_path1"
  vecho "     --tgt-path: $_path2"

  if [ -z "$_path1" ] || [ -z "$_path2" ]; then
    echo_err "--path and --tgt-path arguments are required."
    return 1
  fi

  folders1=$(find "$_path1" -mindepth 1 -maxdepth 1 -type d -printf "%f\n" | sort | uniq)
  folders2=$(find "$_path2" -mindepth 1 -maxdepth 1 -type d -printf "%f\n" | sort | uniq)
	comm -12 <(echo "$folders1") <(echo "$folders2")

  vecho_done "Success."
  return 0
}

gmash_dirs_separate(){
  if [ $# == 0 ]; then
    local _path="${GMASH_DIRS_SEPARATE_PATH:-$(pwd)}"
  else
    local _path="${1:-$(pwd)}"
  fi

  vecho_func "dirs->separate"
  vecho_info "Input Arguments:"
  vecho "     --path: $_path"
  vecho_process "Separating files..."

  for _fp in "$_path"/*; do
    if [ -f "$_fp" ]; then
      _fname="$(basename "$_fp")"
      _dirname="${_fname%.*}"
      mkdir -p "$_path/$_dirname"
      mv "$_fp" "$_path/$_dirname/"
      vecho_action "'$_fp' -> '$_path/$_dirname'"
    fi
  done

  vecho_done "Success."
  return 0
}

gmash_dirs_squash(){
  if [ $# == 0 ]; then
    _root=${GMASH_DIRS_SQUASH_PATH:-"$(pwd)"}
    _depth=${GMASH_DIRS_SQUASH_DEPTH:-1}
  else
    _root=${1:-"$(pwd)"}
    _depth=${2:-1}
  fi

  vecho_func "gmash->dirs->squash"
  vecho_info "Input Arguments:"
  vecho_info "  Root Directory: $_root"
  vecho_info "  Depth: $_depth"

  if [ -z "$_depth" ]; then
    _depth=1
  fi

  if ! [[ "$_depth" =~ ^[0-9]+$ ]]; then
    echo_err "Depth must be a non-negative integer." >&2
    return 1
  fi

  if [ ! -d "$_root" ]; then
    echo_err "Directory '$_root' does not exist." >&2
    return 1
  fi

  vecho_process "Squashing paths."

  _moved_count=0
  _conflict_count=0

  # Find all directories at the specified depth and move their contents to root
  find "$_root" -mindepth "$_depth" -maxdepth "$_depth" -type d -print0 | while IFS= read -r -d '' dir; do
    vecho_action "Processing directory: $dir"

    # Move all files from this directory to root
    shopt -s dotglob nullglob
    for item in "$dir"/*; do
      if [ -e "$item" ]; then
        filename=$(basename "$item")

        # Check for conflicts
        if [ -e "$_root/$filename" ]; then
          vecho_warn "Skipping '$filename' - already exists in root."
          _conflict_count=$((_conflict_count + 1))
          continue
        fi

        # Move the item to root
        if mv "$item" "$_root"/ 2>/dev/null; then
          vecho_action "Moved: '$item' -> '$_root'"
          _moved_count=$((_moved_count + 1))
        else
          vecho_warn "Failed to move: '$item'"
        fi
      fi
    done
    shopt -u dotglob nullglob

    # Remove the empty directory
    if [ -z "$(ls -A "$dir" 2>/dev/null)" ]; then
      rmdir "$dir" 2>/dev/null && vecho_action "Removed empty directory: $dir"
    fi
  done
  vecho_done "Success."
  return 0
}
