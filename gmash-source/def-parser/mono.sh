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
  msg -- "Call [main-cmd] [sub-cmd] --help for details of each sub-command."
  msg -- " "
  msg -- "Sub-Commands:"
  cmd patch \
      -- "Patch a git repository with changes from another branch."
  msg -- " "
  msg -- "Display:"
    standard_parser_help gmash_mono_help
    disp "GMASH_MONO_VERSION" -v --version \
      -- "[$GMASH_MONO_VERSION] Display command group version."
}

gmash_def_parser_mono_patch(){
  extend_parser
  standard_parser_setup GMASH_MONO_PATCH_ARGR gmash_mono_patch_help \
    "Usage: gmash mono patch -r [repo] -b [branch]"
  msg -- "  "
  msg -- "Patch a git repository with changes from another branch."
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