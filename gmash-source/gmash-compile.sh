#!/bin/bash
#@doc##########################################################################
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
###############################################################################
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
###############################################################################
# @file gmash->dirs parser definition
# @created: 2025/08/31
# @brief Run this script in 'gmash-source' dir to generate all gmash parsers.
#@enddoc#######################################################################

readonly GMASH_PARSERS_SRC="$GMASH_SOURCE/def-parser"
readonly GMASH_PARSERS_BIN="$GMASH_SOURCE/parser"

compile_parser(){
  local _command=${1:-""}
  local _subcommand=${2:-""}
  local name_=${_command}
  if [ -n "$_subcommand" ]; then # Append subcommand
    name_="${_command}_${_subcommand}"
  fi
  if [ -z "$name_" ]; then # No args provided, main parser.
    name_="main"
  fi
  # All parsers are defined in the command group source file(or main).
  local src_file_=""
  if [ -n "$_command" ]; then
    src_file_="$_command"
  else
    src_file_=main
  fi

  echo -e "\e[31;1m"  ⚙  Compiling parser $name_ "\e[0m"
  echo "Compiling: 'gengetoptions parser -f \
\"$GMASH_PARSERS_SRC/$src_file_.sh\" \
\"gmash_def_parser_$name_\" \"gmash_parser_$name_\" \
> \"$GMASH_PARSERS_BIN/$src_file_.sh\"'"

  # If its a subcommand, append to the command group parser file.
  if [ -z "$_subcommand" ] ; then
    gengetoptions parser -f "$GMASH_PARSERS_SRC/$src_file_.sh" \
      "gmash_def_parser_$name_" "gmash_parser_$name_" \
        > "$GMASH_PARSERS_BIN/$src_file_.sh"
  else
    gengetoptions parser -f "$GMASH_PARSERS_SRC/$src_file_.sh" \
      "gmash_def_parser_$name_" "gmash_parser_$name_" \
        >> "$GMASH_PARSERS_BIN/$src_file_.sh"
  fi

  echo -e "\e[32m\t  ✓ " "Done." "\e[0m"
}

# Comment out as needed when developing, you only have to regenerate
# the altered parser source. If you change a subcommand, you must
# regenerate the entire command group source.
compile_parser
  compile_parser dirs
    compile_parser dirs prefix
    compile_parser dirs same
    compile_parser dirs separate
    compile_parser dirs squash
  compile_parser find
    compile_parser find duplicate_code
    compile_parser find gits
    compile_parser find sources
  compile_parser gist
    compile_parser gist clone
    compile_parser gist create
    compile_parser gist prepare
    compile_parser gist recover
    compile_parser gist upload
  compile_parser lineage
    compile_parser lineage merge
  compile_parser mono
    compile_parser mono subtree
    compile_parser mono remove
    compile_parser mono pull
    compile_parser mono push
    compile_parser mono config
    compile_parser mono split
