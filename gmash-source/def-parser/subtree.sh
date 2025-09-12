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
source "$GMASH_SOURCE/parser-extensions.sh"

gmash_def_parser_subtree(){
  extend_parser
  standard_parser_setup GMASH_SUBTREE_ARGR gmash_subtree_help \
    "gmash subtree <sub-command> [[args]...]"
  msg -- "Sub-commands:"
  msg -- "Call [main-cmd] [sub-cmd] --help for details of each sub-command."
    cmd new \
      -- "Add and merge a new or existing repo as a subtree to a parent monorepo."
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
    "gmash subtree new"
  msg -- " "
  msg -- "Properly add and merge a new or existing repo as a subtree to a parent monorepo."
  msg -- " "
  msg -- "Parameters:"
    param GMASH_SUBTREE_NEW_URL -l --url var:"<remoteURL>" \
      -- ""
    param GMASH_SUBTREE_NEW_REMOTE -R --remote var:"[remote = \"origin\"]" \
      -- ""
    param GMASH_SUBTREE_NEW_PATH -p --path var:'[subtreePath = <subtreeDirName>]'\
      -- ""
    param GMASH_SUBTREE_NEW_USER -u --user var:'[sourceUser = {currentGithubUser}]' \
      -- ""
    param GMASH_SUBTREE_NEW_TGTUSER -U --tgt-user var:'[targetUser = <sourceUser>]' \
      -- ""
    param GMASH_SUBTREE_NEW_BR -b --branch var:"[monoBranch = \"main\"]" \
      -- ""
    param GMASH_SUBTREE_NEW_TGTBR -B --tgt-branch var:"[subtreeBranch = \"main\"]" \
      -- ""
    param GMASH_SUBTREE_NEW_NAME -n --name var:'[subtreeDirName = <remoteName>]' \
      -- ""
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
    param GMASH_SUBTREE_PATCH_REMOTE -R --remote var:"[remote = \"origin\"]" \
      -- ""
    param GMASH_SUBTREE_PATCH_BRANCH -b --branch var:"[branch = \"main\"]" \
      -- ""
    param GMASH_SUBTREE_PATCH_PATH -p --path var:"<subtreePath>"\
      -- ""
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_subtree_patch_help
    disp "GMASH_SUBTREE_PATCH_VERSION" -v --version \
      -- "[$GMASH_SUBTREE_PATCH_VERSION] Display command group version."
}