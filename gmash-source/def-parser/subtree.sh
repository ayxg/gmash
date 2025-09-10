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

gmash_def_parser_subtree(){
  extend_parser
  standard_parser_setup GMASH_SUBTREE_ARGR gmash_subtree_help \
    "gmash subtree <sub-command> [[args]...]"
  msg -- "Sub-commands:"
  msg -- "Call [main-cmd] [sub-cmd] --help for details of each sub-command."
    cmd new \
      -- "Properly add and merge a new or existing repo as a subtree to a parent monorepo."
    cmd patch \
      -- "Patch subtree changes to monorepo."
  msg -- "Display:"
    standard_parser_help gmash_subtree_help
    disp "GMASH_SUBTREE_VERSION" -v --version \
      -- "[$GMASH_SUBTREE_VERSION] Display command group version."
}

gmash_def_parser_subtree_new(){
  extend_parser
  standard_parser_setup GMASH_SUBTREE_NEW_ARGR gmash_subtree_new_help \
    "gmash subtree new -r [repo] -b [branch]"
  msg -- "Description:"
  msg -- "Properly add and merge a new or existing repo as a subtree to a parent monorepo."
  msg -- "Parameters:"
    param GMASH_SUBTREE_NEW_REPO -r --repo var:"<repo>" \
      -- "Target repository."
    param GMASH_SUBTREE_NEW_BRANCH -b --branch var:"<branch>" \
      -- "Target branch."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_subtree_new_help
    disp "GMASH_SUBTREE_NEW_VERSION" -v --version \
      -- "[$GMASH_SUBTREE_NEW_VERSION] Display command group version."
}

gmash_def_parser_subtree_patch(){
  extend_parser
  standard_parser_setup GMASH_SUBTREE_PATCH_ARGR gmash_subtree_patch_help \
    "gmash subtree patch -r [repo] -b [branch]"
  msg -- "Description:"
  msg -- "Patch subtree changes to monorepo."
  msg -- "Parameters:"
    param GMASH_SUBTREE_PATCH_REPO -r --repo var:"<repo>" \
      -- "Target repository."
    param GMASH_SUBTREE_PATCH_BRANCH -b --branch var:"<branch>" \
      -- "Target branch."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_subtree_patch_help
    disp "GMASH_SUBTREE_PATCH_VERSION" -v --version \
      -- "[$GMASH_SUBTREE_PATCH_VERSION] Display command group version."
}