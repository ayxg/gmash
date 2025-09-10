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
# @created: 2025/09/02
#@enddoc###########################################################################################
source "$(dirname "$(readlink -f "$0")")/gmash-source/parser-extensions.sh"

gmash_def_parser_lineage(){
  extend_parser
  standard_parser_setup GMASH_LINEAGE_ARGR gmash_lineage_help \
    "gmash lineage <sub-command> [[args]...]"
  msg -- "Sub-commands:"
  msg -- "Call [main-cmd] [sub-cmd] --help for details of each sub-command."
    cmd merge \
      -- "Merge git commits from multiple git repos in a straight lineage."
  msg -- "Display:"
    standard_parser_help gmash_lineage_help
    disp "GMASH_LINEAGE_VERSION" -v --version \
      -- "[$GMASH_LINEAGE_VERSION] Display command group version."
}


gmash_def_parser_lineage_merge(){
  extend_parser
  standard_parser_setup GMASH_LINEAGE_MERGE_ARGR gmash_lineage_merge_help \
    "gmash lineage merge -r [repo] -b [branch]"
  msg -- "Description:"
  msg -- "Merge git commits from multiple git repos in a straight lineage."
  msg -- "Parameters:"
    param GMASH_LINEAGE_MERGE_REPO -r --repo var:"<repo>" \
      -- "Target repository."
    param GMASH_LINEAGE_MERGE_BRANCH -b --branch var:"<branch>" \
      -- "Target branch."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_lineage_merge_help
    disp "GMASH_LINEAGE_MERGE_VERSION" -v --version \
      -- "[$GMASH_LINEAGE_MERGE_VERSION] Display command group version."
}