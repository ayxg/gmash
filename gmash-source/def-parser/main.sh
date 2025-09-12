#!/bin/bash
#@doc##########################################################################
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
###############################################################################
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
###############################################################################
# @file gmash main parser
# @created: 2025/09/02
#@enddoc#######################################################################

source "$(dirname "$(readlink -f "$0")")/gmash-source/parser-extensions.sh"

# Main 'gmash' cli args parser.
# This parse step only parses the main command, then dispatches to a command specific parse step.
# The functionality of flags and options is dependant on which main command is called.
# @see gmash_dispatch_parsers
gmash_def_parser_main() {
  msg -- "gmash $GMASH_VERSION"
  msg -- "$GMASH_LICENSE"
  msg -- "Smash keyboard - get git. Bash scripts for high-level git & github repo management."
  msg -- "  "
  extend_parser
  standard_parser_setup GMASH_ARGR gmash_main_help \
    "Usage: gmash [[global-args]...] <main-command> <sub-command> [[args]...]"
  msg -- "  "
  msg -- "Globals:"
    flag GMASH_VERBOSE -V --verbose init:=0 -- "Globally enable verbose output."
    flag GMASH_QUIET   -Q --quiet   init:=0 -- "Globally disable output. !Warning: some command outputs may be suppressed."
    param GMASH_CONFIG -c --config  var:"<gmashConfigFile>" init:=".gmashuser" -- "Use a gmash argument config file."
  msg -- "  "
  msg -- "Commands:"
    cmd dirs \
      -- "High level path/file manipulation and analysis."
        msg -- "  prefix          Add a prefix to each top-level file in a directory."
        msg -- "  same            Get a diff of 2 directories."
        msg -- "  separate        Separate a directory into its constituent parts."
        msg -- "  squash          Squash empty paths in a directory."
        msg -- "  "
    cmd find \
      -- "High level file/repo/code searching and analysis."
        msg -- "  duplicate-code  Find duplicate code across files."
        msg -- "  gits            Find git repositories."
        msg -- "  sources         Find source files."
        msg -- "  "
    cmd gist \
      -- "Manage GitHub Gists with git-like functionality, integrates with 'mono' && 'subtree'."
        msg -- "  prepare         Sets up a new gist with a title.md page with the same name as the target source file(s)."
        msg -- "  create          Push all files in a directory as gists to GitHub. Adds a title.md and readme.md by default."
        msg -- "  clone           Clones a gist to the local filesystem."
        msg -- "  recover         Recover a user's gist(s) from GitHub remotes as git repos."
        msg -- "  upload          Upload files to existing gists."
        msg -- "  "
    cmd lineage \
      -- "Amalgamate git commits from archived git repos to a more recent version."
    cmd mono \
      -- "Manage Monorepo->Subtree github git remotes and locals."
    cmd subtree \
      -- "Manage Subtree->Monorepo github git remotes and locals."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_main_help
    disp "GMASH_VERSION" -v --version -- "[$GMASH_VERSION] Display gmash, command or subcommand version."
    disp :gmash_versions_index --versions -- "Display versions of gmash and all commands/subcommands."
  msg -- "  "
  msg -- "Development:"
  msg -- "    --compile-parser        Compile command line parser source files."
  msg -- "  "

}