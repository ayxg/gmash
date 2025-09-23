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
# @created: 2025/09/02
#@enddoc#######################################################################
source "$GMASH_SOURCE/parser-extensions.sh"

# gmash_def_parser_dirs --> gmash_parser_dirs
gmash_def_parser_dirs(){
  extend_parser
  standard_parser_setup GMASH_DIRS_ARGR gmash_dirs_help \
    "Usage: gmash dirs <sub-command> [[args]...]"
  msg -- "  "
  msg -- "High level path/file manipulation and analysis."
  msg -- "  "
  msg -- "Sub-commands:"
    cmd prefix -- "Add a prefix to each top-level file in a directory."
    cmd same -- "Get a diff of 2 directories."
    cmd separate -- "Separate a directory into its constituent parts."
    cmd squash -- "Squash empty paths in a directory."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_dirs_help
    disp "GMASH_DIRS_VERSION" -v --version \
      -- "[$GMASH_DIRS_VERSION] Display command group version."
}

gmash_def_parser_dirs_prefix(){
  extend_parser
  standard_parser_setup GMASH_DIRS_PREFIX_ARGR gmash_dirs_prefix_help \
    "Usage: gmash dirs prefix --p <prefix> --P [fileOrFolder]"
  msg -- "  "
  msg -- "Add a prefix to each top-level file in a directory."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_DIRS_PREFIX_PREFIX -p --prefix var:"<prefix>" -- "Prefix to add."
    param GMASH_DIRS_PREFIX_PATH -P --path var:"[fileOrFolder]" -- "Path to a file\
 or directory. If given a file, only the single file is prefixed."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_dirs_prefix_help
    disp "GMASH_DIRS_PREFIX_VERSION" -v --version \
      -- "[$GMASH_DIRS_PREFIX_VERSION] Display command group version."
}

gmash_def_parser_dirs_same(){
  extend_parser
  standard_parser_setup GMASH_DIRS_SAME_ARGR gmash_dirs_same_help \
    "Usage: gmash dirs same -p <srcPath> -P <tgtPath>"
  msg -- "  "
  msg -- "Get a diff of 2 directories."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_DIRS_SAME_PATH -p --path var:"<srcPath>" -- "Source path."
    param GMASH_DIRS_SAME_TGTPATH -P --tgt-path var:"<tgtPath>" -- "Target path."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_dirs_same_help
    disp "GMASH_DIRS_SAME_VERSION" -v --version \
      -- "[$GMASH_DIRS_SAME_VERSION] Display command group version."
}

gmash_def_parser_dirs_separate(){
  extend_parser
  standard_parser_setup GMASH_DIRS_SEPARATE_ARGR gmash_dirs_separate_help \
    "Usage: gmash dirs separate [path]"
  msg -- "  "
  msg -- "Separate each top-level file into its own folder of the same name."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_DIRS_SEPARATE_PATH -p --path var:"[path]" -- "Path to separate files from. Defaults to current."
  msg -- "  "
  msg -- "Options:"
    param GMASH_DIRS_SEPARATE_NOEXTENSION -n --no-extension var:""\
      -- "Separate files with the same base name, ignoring extensions."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_dirs_separate_help
    disp "GMASH_DIRS_SEPARATE_VERSION" -v --version \
      -- "[$GMASH_DIRS_SEPARATE_VERSION] Display command group version."
}

gmash_def_parser_dirs_squash(){
  extend_parser
  standard_parser_setup GMASH_DIRS_SQUASH_ARGR gmash_dirs_squash_help \
    "Usage: gmash dirs squash [path]"
  msg -- "  "
  msg -- "Squash empty directories in the specified path."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_DIRS_SQUASH_PATH -p --path var:"[path]" \
      -- "Target path. Defaults to current."
    param GMASH_DIRS_SQUASH_DEPTH -d --depth var:"[depth]" \
      -- "Depth of directories to squash. Defaults to 1."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_dirs_squash_help
    disp "GMASH_DIRS_SQUASH_VERSION" -v --version \
      -- "[$GMASH_DIRS_SQUASH_VERSION] Display command group version."
}