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
    "gmash mono <sub-command> [[args]...]"
  msg -- "Sub-commands:"
  msg -- "Call [main-cmd] [sub-cmd] --help for details of each sub-command."
  cmd patch \
      -- "Patch a git repository with changes from another branch."
  msg -- "Display:"
    standard_parser_help gmash_mono_help
    disp "GMASH_MONO_VERSION" -v --version \
      -- "[$GMASH_MONO_VERSION] Display command group version."
}

gmash_def_parser_mono_patch(){
  extend_parser
  standard_parser_setup GMASH_MONO_PATCH_ARGR gmash_mono_patch_help \
    "gmash mono patch -r [repo] -b [branch]"
  msg -- "Description:"
  msg -- "Patch a git repository with changes from another branch."
  msg -- "Parameters:"
    param GMASH_MONO_PATCH_REPO -r --repo var:"<repo>" \
      -- "Target repository."
    param GMASH_MONO_PATCH_BRANCH -b --branch var:"<branch>" \
      -- "Target branch."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_mono_patch_help
    disp "GMASH_MONO_PATCH_VERSION" -v --version \
      -- "[$GMASH_MONO_PATCH_VERSION] Display command group version."
}