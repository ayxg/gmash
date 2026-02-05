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

gmash_def_parser_mono(){
  extend_parser
  standard_parser_setup GMASH_MONO_ARGR gmash_mono_help \
    "Usage: gmash mono <sub-command> [[args]...]"
  msg -- " "
  msg -- "Git+GitHub monorepo workflow strategy."
  msg -- "Call [main-cmd] [sub-cmd] --help for details of each sub-command."
  msg -- " "
  msg -- "Sub-Commands:"
  cmd subtree \
    -- "Add or re-configure a sub project to the mono repo as a subtree."
  cmd remove \
    -- "Remove a subtree from the monorepo."
  cmd pull \
    -- "Pull changes from a sub project's remote into the mono repo."
  cmd push \
    -- "Push changes in the mono repo to a sub project's remote."
  cmd config \
    -- "Configure a mono repo's remotes based on stored subproject metadata."
  cmd clone \
    -- "Clone repo from remote or local and add subtrees based on stored metadata."
  msg -- " "
  msg -- "Display:"
    standard_parser_help gmash_mono_help
    disp "GMASH_MONO_VERSION" -v --version \
      -- "[$GMASH_MONO_VERSION] Display command group version."
}

gmash_def_parser_mono_subtree(){
  extend_parser
  standard_parser_setup GMASH_MONO_SUBTREE_ARGR gmash_mono_subtree_help \
    "Usage: gmash mono subtree <-p <subtreePrefixPath>> <-r <remoteAlias>> <-l <remoteUrl>> [-b <subtreeBranch>]"
  msg -- " "
  msg -- "Add or re-configure a sub project to the mono repo as a subtree."
  msg -- " "
  msg -- "Parameters:"
    param GMASH_MONO_SUBTREE_PREFIX -p --prefix var:'<subtreePrefixPath>'\
      -- "Relative path inside the parent repo where the subtree will be added. Cannot be\
 the root path. The path must be empty or non-existent in the parent repo. gmash will deny\
 adding a subtree to a path which already contains any files."
    param GMASH_MONO_SUBTREE_REMOTE -r --remote var:"<remoteAlias>" \
      -- "Remote alias to add to the parent repo, which will be refered to when pulling\
 and pushing changes to the added subtree."
    param GMASH_MONO_SUBTREE_URL -l --url var:"<remoteURL>" \
      -- "Remote repository URL of the subtree to add. Ignored if '--new' is passed."
    param GMASH_MONO_SUBTREE_BR -b --branch var:"<subtreeBranch>"\
      -- "Target branch of the subtree remote to pull in."
    flag GMASH_MONO_SUBTREE_SQUASH -s --squash var:"" \
      -- "Instead of merging the entire history from the subtree project, produce only\
 a single commit that contains all the differences to merge. Then, merge that new\
 commit into the parent repo. Note, if you add a subtree with --squash, future
 pulls and pushes to that subtree should also be squashed."
    flag GMASH_MONO_SUBTREE_NEW -n --new var:"" \
      -- "Create a new github repo for the added subtree. Requires '--name' and '--owner'\
 to be specified."
    param GMASH_MONO_SUBTREE_NAME -N --name var:"<subtreeRepoName>" \
      -- "Name of the new remote repo to create for the subtree. Required if '--new' is\
 passed."
    param GMASH_MONO_SUBTREE_OWNER -O --owner var:"<subtreeRepoOwner>" \
      -- "Owner (user or org) of the new remote repo to create for the subtree. Required if\
 '--new' is passed."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_mono_subtree_help
    disp "GMASH_MONO_SUBTREE_VERSION" -v --version \
      -- "[$GMASH_MONO_SUBTREE_VERSION] Display command group version."
}

gmash_def_parser_mono_remove(){
  extend_parser
  standard_parser_setup GMASH_MONO_REMOVE_ARGR gmash_mono_remove_help \
    "Usage: gmash mono remove -r [remote] -p [prefix] [-k]"
  msg -- "  "
  msg -- "Remove a subtree from the monorepo."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_MONO_REMOVE_REMOTE -r --remote var:"<subtreeRemote>" \
      -- "Target subtree remote alias."
    param GMASH_MONO_REMOVE_PREFIX -p --prefix var:"<subtreePrefixPath>"\
      -- "Subtree prefix path in the monorepo. Prefer not to specify this and let gmash look it up from metadata."
    flag GMASH_MONO_REMOVE_KEEP_REMOTE -k --keep-remote var:"" \
      -- "Keep the remote alias in the parent repo even if it is no longer used."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_mono_remove_help
    disp "GMASH_MONO_REMOVE_VERSION" -v --version \
      -- "[$GMASH_MONO_REMOVE_VERSION] Display command group version."
}

gmash_def_parser_mono_pull(){
  extend_parser
  standard_parser_setup GMASH_MONO_PULL_ARGR gmash_mono_pull_help \
    "Usage: gmash mono pull -r [repo] -b [branch]"
  msg -- "  "
  msg -- "Pull subtree changes to monorepo."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_MONO_PULL_REMOTE -r --remote var:"<subtreeRemote>" \
      -- "Target subtree remote alias."
    param GMASH_MONO_PULL_BRANCH -b --branch var:"<subtreeBranch>" \
      -- "Target subtree branch."
    param GMASH_MONO_PULL_PREFIX -p --prefix var:"<subtreePrefixPath>"\
      -- "Subtree prefix path in the monorepo."
    flag GMASH_MONO_PULL_ALL -a --all var:""\
      -- "Patch all subtrees based on gmash metadata."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_mono_pull_help
    disp "GMASH_MONO_PULL_VERSION" -v --version \
      -- "[$GMASH_MONO_PULL_VERSION] Display command group version."
}

gmash_def_parser_mono_push(){
  extend_parser
  standard_parser_setup GMASH_MONO_PATCH_ARGR gmash_mono_patch_help \
    "Usage: gmash mono push -r [repo] -b [branch]"
  msg -- "  "
  msg -- "Push changes in the mono repo to a sub project's remote."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_MONO_PATCH_BR -b --br var:"<monoBranch>" \
      -- "Source mono branch to pull changes from."

    param GMASH_MONO_PATCH_PATH -p --path var:"<prefixPath>" \
      -- "Subtree prefix path in the monorepo."

    param GMASH_MONO_PATCH_REMOTE -r --remote var:"<subtreeRemote>" \
      -- "Target subtree remote alias."

    param GMASH_MONO_PATCH_TGTBR -B --tgtbr var:"<subtreeBranch>" \
      -- "Target subtree remote alias."

    param GMASH_MONO_PATCH_TGTUSER -U --tgtuser var:"<subtreeOwner>" \
      -- "Owner of the target subtree repo."

    param GMASH_MONO_PATCH_TEMPBR -t --tempbr var:"<tempBranch>" \
      -- "Owner of the target subtree repo."

    param GMASH_MONO_PATCH_TEMPDIR -T --tempdir var:"<tempPath>" \
      -- "Owner of the target subtree repo."

    param GMASH_MONO_PATCH_USER -u --user var:"<tempPath>" \
      -- "Owner the mono repo. Defaults to current GitHub user."

    param GMASH_MONO_PATCH_URL -l --url var:"<repo>" \
      -- "Target repository."

    flag GMASH_MONO_PATCH_ALL -a --all var:"" \
      -- "Patch all known subtrees in the mono repo."

    flag GMASH_MONO_PATCH_MAKEPR -P --make-pr var:"" \
      -- "Make a pull request on GitHub with the patched changes."

    flag GMASH_MONO_PATCH_SQUASH -s --squash var:"" \
      -- "Squash strategy when merging subtree changes. Must be consistent with\
  the previous pul of the subtree."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_mono_patch_help
    disp "GMASH_MONO_PATCH_VERSION" -v --version \
      -- "[$GMASH_MONO_PATCH_VERSION] Display command group version."
}

gmash_def_parser_mono_config(){
  extend_parser
  standard_parser_setup GMASH_MONO_CONFIG_ARGR gmash_mono_config_help \
    "Usage: gmash mono config -r [repo] -b [branch]"
  msg -- "  "
  msg -- "Configure a mono repo's remotes based on stored subproject metadata."
  msg -- "  "
  msg -- "Parameters:"
    param GMASH_MONO_CONFIG_REMOTE -r --remote var:"<subtreeRemote>" \
      -- "Target subtree remote alias."
    param GMASH_MONO_CONFIG_BRANCH -b --branch var:"<subtreeBranch>" \
      -- "Target subtree branch."
    param GMASH_MONO_CONFIG_PREFIX -p --prefix var:"<subtreePrefixPath>"\
      -- "Subtree prefix path in the monorepo."
    flag GMASH_MONO_CONFIG_ALL -a --all var:""\
      -- "Configure all subtrees based on gmash metadata."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_mono_config_help
    disp "GMASH_MONO_CONFIG_VERSION" -v --version \
      -- "[$GMASH_MONO_CONFIG_VERSION] Display command group version."
}