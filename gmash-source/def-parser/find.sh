#!/bin/bash
#@doc##########################################################################
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
###############################################################################
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
###############################################################################
# @file gmash->find parser definition
# @created: 2025/09/02
#@enddoc#######################################################################
source "$GMASH_SOURCE/parser-extensions.sh"

# gmash_def_parser_find --> gmash_parser_find
gmash_def_parser_find(){
  extend_parser
  standard_parser_setup GMASH_FIND_ARGR gmash_find_help \
    "Usage: gmash [[global-args]...] find <sub-command> [[args]...]"
  msg -- "  "
  msg -- "High level path/file manipulation and analysis."
  msg -- "  "
  msg -- "Sub-commands:"
    cmd duplicate-code      -- "Find duplicate code across files."
    cmd gits                -- "Find git repositories."
    cmd sources             -- "Find source files."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_find_help
    disp "GMASH_FIND_VERSION" -v --version \
      -- "[$GMASH_FIND_VERSION] Display command group version."
}

gmash_def_parser_find_duplicate_code(){
  extend_parser
  standard_parser_setup GMASH_FIND_DUPLICATE_CODE_ARGR gmash_find_duplicate_code_help \
    "gmash find duplicate-code -p [path] -t [threshold]"
  msg -- "  "
  msg -- "Uses 'simian' java lib to detect duplicate C++ files in a directory tree."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_FIND_DUPLICATE_CODE_PATH -p --path var:"<path>"\
      -- "Target path."
    param GMASH_FIND_DUPLICATE_CODE_THRESHOLD -t --threshold var:"<threshold>" \
      -- "Duplicate line threshold."
  msg -- "  "
  msg -- "'simian' java lib additional options:"
  msg -- "$(java -jar /c/lib/simian-4.0.0/simian-4.0.0.jar --help | sed 's/^/  /')"
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_find_duplicate_code_help
    disp "GMASH_FIND_DUPLICATE_CODE_VERSION" -v --version \
      -- "[$GMASH_FIND_DUPLICATE_CODE_VERSION] Display command group version."
}

gmash_def_parser_find_sources(){
  extend_parser
  standard_parser_setup GMASH_FIND_SOURCES_ARGR gmash_find_sources_help \
    "gmash find sources -p [path]"
  msg -- "  "
  msg -- "Find source files in a directory tree."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_FIND_SOURCES_PATH -p --path var:"<path>" \
      -- "Target path."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_find_sources_help
    disp "GMASH_FIND_SOURCES_VERSION" -v --version \
      -- "[$GMASH_FIND_SOURCES_VERSION] Display command group version."
}

gmash_def_parser_find_gits(){
  extend_parser
  standard_parser_setup GMASH_FIND_GITS_ARGR gmash_find_gits_help \
    "gmash find gits -p [path]"
  msg -- "  "
  msg -- "Find git repositories in a directory tree."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_FIND_GITS_PATH -p --path var:"<path>" \
      -- "Target path."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_find_gits_help
    disp "GMASH_FIND_GITS_VERSION" -v --version \
      -- "[$GMASH_FIND_GITS_VERSION] Display command group version."
}
