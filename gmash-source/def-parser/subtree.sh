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
    "Usage: gmash subtree <sub-command> [[args]...]"
  msg -- " "
  msg -- "Call [main-cmd] [sub-cmd] --help for details of each sub-command."
  msg -- " "
  msg -- "Sub-Commands:"
    cmd new \
      -- "Add and merge a new or existing repo as a subtree to a parent monorepo."
    cmd patch \
      -- "Patch subtree changes to monorepo."
  msg -- " "
  msg -- "Display:"
    standard_parser_help gmash_subtree_help
    disp "GMASH_SUBTREE_VERSION" -v --version \
      -- "[$GMASH_SUBTREE_VERSION] Display command group version."
}

gmash_def_parser_subtree_new(){
  extend_parser
  standard_parser_setup GMASH_SUBTREE_NEW_ARGR gmash_subtree_new_help \
    "Usage: gmash subtree new <-p <subtreePrefixPath>> <-r <remoteAlias>> <-l <remoteUrl>> [-b <subtreeBranch>]"
  msg -- " "
  msg -- "Properly add and merge a new or existing repo as a subtree to a parent monorepo."
  msg -- " "
  msg -- "Parameters:"
    param GMASH_SUBTREE_NEW_PREFIX -p --prefix var:'<subtreePrefixPath>'\
      -- "Relative path inside the parent repo where the subtree will be added. Cannot be\
 the root path. The path must be empty or non-existent in the parent repo. gmash will deny\
 adding a subtree to a path which already contains any files."
     param GMASH_SUBTREE_NEW_REMOTE -r --remote var:"<remoteAlias>" \
      -- "Remote alias to add to the parent repo, which will be refered to when pulling\
 and pushing changes to the added subtree."
     param GMASH_SUBTREE_NEW_URL -l --url var:"<remoteURL>" \
      -- "Remote repository URL of the subtree to add. If not provided, gmash will\
 attempt to find an existing GitHub repo at 'api-user/remote.git'. If no such\
 repo exists and '--new' is passed: a new empty repo will be created at\
 'api-user/remote.git'."
    param GMASH_SUBTREE_NEW_BR -b --branch var:"[monoBranch = \"main\"]" \
      -- "Target branch of the subtree remote to pull in. Defaults to 'main'."
    flag GMASH_SUBTREE_NEW_SQUASH -s --squash var:"" \
      -- "Instead of merging the entire history from the subtree project, produce only\
 a single commit that contains all the differences to merge. Then, merge that new\
 commit into the parent repo. Note, if you add a subtree with --squash, future
 pulls and pushes to that subtree should also be squashed."
    flag GMASH_SUBTREE_ADD_NEW -n --new var:"" \
      -- "Create a new github repo for the added subtree, if the target subtree remote\
 does not exist."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_subtree_new_help
    disp "GMASH_SUBTREE_NEW_VERSION" -v --version \
      -- "[$GMASH_SUBTREE_NEW_VERSION] Display command group version."
}

gmash_def_parser_subtree_patch(){
  extend_parser
  standard_parser_setup GMASH_SUBTREE_PATCH_ARGR gmash_subtree_patch_help \
    "Usage: gmash subtree patch -r [repo] -b [branch]"
  msg -- "  "
  msg -- "Pull subtree changes to monorepo."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_SUBTREE_PATCH_REMOTE -R --remote var:"[remote = \"origin\"]" \
      -- "Target subtree remote alias. Defaults to 'origin'."
    param GMASH_SUBTREE_PATCH_BRANCH -b --branch var:"[branch = \"main\"]" \
      -- "Target subtree branch. Defaults to 'main'."
    param GMASH_SUBTREE_PATCH_PATH -p --path var:"<subtreePath>"\
      -- "Subtree prefix path in the monorepo."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_subtree_patch_help
    disp "GMASH_SUBTREE_PATCH_VERSION" -v --version \
      -- "[$GMASH_SUBTREE_PATCH_VERSION] Display command group version."
}