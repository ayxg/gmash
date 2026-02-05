#!/bin/bash
#@doc---------------------------------------------------------------------------------------------#
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
#-------------------------------------------------------------------------------------------------#
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
#-------------------------------------------------------------------------------------------------#
# @file GMash main source script.
# @created: 2025/08/31
# @brief Smash keyboard - get git. Bash scripts for high-level git & github repo management.
#
# Conventions:
# - Func prefix [gmash_]
# - Global vars prefix [GMASH_]
# - Local func vars prefix [_]
#@enddoc------------------------------------------------------------------------------------------#

# Source path (used for relative sources)
export GMASH_SOURCE="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Program Metadata
export GMASH_PROGRAM="${0##*/}"
export GMASH_LICENSE="AGPL-3.0-or-later Copyright(c) 2025 Anton Yashchenko"

# Global Vars.
export GMASH_ARGV=("$@")  # Initial input args.
export GMASH_ARGC="$#"    # Initial input args count.
export GMASH_ARGR=""      # Rest of unparsed args ,set by getoptions parsers.

# Global main parser vars.
export GMASH_VERBOSE=0
export GMASH_QUIET=0
export GMASH_CONFIG=""    # Config file path.

  # Version metadata
  export GMASH_VERSION="v0-0-0"
    export GMASH_DIRS_VERSION="v0-0-0"
      export GMASH_DIRS_PREFIX_VERSION="v0-0-0"
      export GMASH_DIRS_SAME_VERSION="v0-0-0"
      export GMASH_DIRS_SEPARATE_VERSION="v0-0-0"
      export GMASH_DIRS_SQUASH_VERSION="v0-0-0"

    export GMASH_FIND_VERSION="v0-0-0"
      export GMASH_FIND_DUPLICATE_CODE_VERSION="v0-0-0"
      export GMASH_FIND_GITS_VERSION="v0-0-0"
      export GMASH_FIND_SOURCES_VERSION="v0-0-0"

    export GMASH_GIST_VERSION="v0-0-0"
      export GMASH_GIST_CLONE_VERSION="v0-0-0"
      export GMASH_GIST_CREATE_VERSION="v0-0-0"
      export GMASH_GIST_PREPARE_VERSION="v0-0-0"
      export GMASH_GIST_RECOVER_VERSION="v0-0-0"
      export GMASH_GIST_UPLOAD_VERSION="v0-0-0"

    export GMASH_LINEAGE_VERSION="v0-0-0"
      export GMASH_LINEAGE_MERGE_VERSION="v0-0-0"

    export GMASH_MONO_VERSION="v0-0-0"
      export GMASH_MONO_SUBTREE_VERSION="v0-0-0"
      export GMASH_MONO_REMOVE_VERSION="v0-0-0"
      export GMASH_MONO_PULL_VERSION="v0-0-0"
      export GMASH_MONO_CONFIG_VERSION="v0-0-0"
      export GMASH_MONO_PATCH_VERSION="v0-0-0"

gmash_versions_index(){
  echo "gmash $GMASH_VERSION"
    echo "  dirs $GMASH_DIRS_VERSION"
      echo "    prefix $GMASH_DIRS_PREFIX_VERSION"
      echo "    same $GMASH_DIRS_SAME_VERSION"
      echo "    separate $GMASH_DIRS_SEPARATE_VERSION"
      echo "    squash $GMASH_DIRS_SQUASH_VERSION"
  echo "  find $GMASH_FIND_VERSION"
    echo "    duplicate-code $GMASH_FIND_DUPLICATE_CODE_VERSION"
    echo "    gits $GMASH_FIND_GITS_VERSION"
    echo "    sources $GMASH_FIND_SOURCES_VERSION"
  echo "  gist $GMASH_GIST_VERSION"
    echo "    clone $GMASH_GIST_CLONE_VERSION"
    echo "    create $GMASH_GIST_CREATE_VERSION"
    echo "    prepare $GMASH_GIST_PREPARE_VERSION"
    echo "    recover $GMASH_GIST_RECOVER_VERSION"
    echo "    upload $GMASH_GIST_UPLOAD_VERSION"
  echo "  lineage $GMASH_LINEAGE_VERSION"
    echo "    merge $GMASH_LINEAGE_MERGE_VERSION"
  echo "  mono $GMASH_MONO_VERSION"
    echo "    subtree $GMASH_MONO_SUBTREE_VERSION"
    echo "    pull $GMASH_MONO_PULL_VERSION"
    echo "    config $GMASH_MONO_CONFIG_VERSION"
    echo "    push $GMASH_MONO_PATCH_VERSION"
}
