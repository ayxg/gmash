#!/bin/bash
#@doc##############################################################################################
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
###################################################################################################
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
###################################################################################################
# @file
# @created: 2025/08/31
# @brief Extensions for getoptions library parsers.
#@enddoc###########################################################################################

# Source the global vars so they are available to the parser definitions. The parser definitions
# are pre-generated(compiled) then used in the main script.
source "$(dirname "$(readlink -f "$0")")/gmash-source/global.sh"

# Set as getoptions parser error callback.
parser_error() {
  echo -e "\e[31;1mError:\e[0m $*" >&2;
}

# Use 'array' param type inside a parser definition to accept multiple args.
# Example:
#    array ARGV_FILE -f --file init:'ARGV_FILE=()' var:"<filePath>"\
#      -- "File(s) to upload to the gist."
#
# TODO: figure out how to accept multiple args for a single option.
#       For now we accept 1 per-option allowing multiple occurences.
#       (such a bash noob...)
append_array() {
	eval "$1+=(\"\$OPTARG\")"
}

# @func extend_parser
# Additional getoptions arg types and default setup for gmash getoptions parsers.
# Includes the setup and display lines. Add at the start of each parser definition.
extend_parser(){
  # Custom array param.
  # @see append_array for details.
	array() { param ":append_array $@"; }

  # $1 = <flagName> : The name of the flag variable to create.
  # $2 = <short>    : The short option name.
  # $3 = <long>     : The long option name.
  # $4 = <comment>  : The comment to display in the help output.
  gmash_flag(){
    flag $1 $2 $3 on:1 no:1 init:="0" \
      -- "$4"
  }

  # $1 : <helpFunctionName> : This function will be generated, outputs the help for this parser.
  # $2 = <titleText>        : Main title text, included in the help output.
  standard_parser_setup(){
    setup \
      $1 \
      error:parser_error \
      export:true \
      plus:true \
      width:40 \
      help:$2 \
      abbr:true \
      -- "$3"
  }

  # $1 : <helpFunctionName> : This should be the same function that was passed to standard_parser_setup.
  standard_parser_help(){
    disp    ":$1" -h --help -- "Display gmash, command or subcommand help. Use -h or --help."
  }

}