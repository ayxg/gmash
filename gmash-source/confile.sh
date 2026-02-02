#!/bin/bash
#@doc---------------------------------------------------------------------------------------------#
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
#-------------------------------------------------------------------------------------------------#
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
#-------------------------------------------------------------------------------------------------#
# @file confile.sh
# @created: 2025/09/26
# @brief Basic key-value configuration file handler for gmash.
#   Write: confwrite <file> <key> <value>
#   Read: confread <file> <key>
#@enddoc------------------------------------------------------------------------------------------#

readonly CONFILE_VERSION=1

# Read a key value from a config file.
# $1 = config file path
# $2 = key to read
confread() {
  local _file="$1"
  local _key="$2"
  if [[ -f "$_file" ]]; then
    grep "^$_key=" "$_file" | cut -d'=' -f2-
  else
      echo "Config file '$_file' does not exist."
  fi
}

# Write a key value to a config file.
# $1 = config file path
# $2 = key
# $3 = value
confwrite() {
    local _path="$1"
    local _key="$2"
    local _value="$3"
    local _dir

    _dir=$(dirname "$_path")

    if [ ! -d "$_dir" ]; then
        mkdir -p "$_dir"
    fi

    if [ ! -f "$_path" ]; then
        touch "$_path"
    fi

    if [[ -f "$_path" ]] && grep -q "^$_key=" "$_path"; then
        sed -i "s/^$_key=.*/$_key=$_value/" "$_path"    # Update existing
    else
        echo "$_key=$_value" >> "$_path"                # Add new
    fi
}
