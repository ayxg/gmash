#!/bin/bash
#@doc##########################################################################
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
###############################################################################
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
###############################################################################
# @file gmash->lineage command group
# @created: 2025/08/31
#@enddoc#######################################################################

gmash_lineage_merge(){
  # ==== CONFIGURATION ====
  # Paths to repos (local .git directories or remote URLs)
  CURRENT_REPO="/path/to/current.git"
  OLD1="/path/to/old1.git"
  OLD2="/path/to/old2.git"
  OLD3="/path/to/old3.git"
  OLD4="/path/to/old4.git"

  WORKDIR="./merged-history"   # where we’ll build the combined repo

  # ==== SCRIPT START ====
  rm -rf "$WORKDIR"
  git clone "$CURRENT_REPO" "$WORKDIR"
  cd "$WORKDIR"

  function graft_repo {
      local NAME=$1
      local URL=$2
      local PREV_LAST=$3

      echo "=== Adding $NAME ==="
      git remote add "$NAME" "$URL"
      git fetch "$NAME"

      # First commit of new repo
      NEW_FIRST=$(git log "$NAME/master" --reverse --format="%H" | head -n 1)
      # Last commit of new repo
      NEW_LAST=$(git log "$NAME/master" --format="%H" | head -n 1)

      echo "→ First commit of $NAME: $NEW_FIRST"
      echo "→ Last commit of $NAME: $NEW_LAST"

      if [ -n "$PREV_LAST" ]; then
          echo "Grafting: make $NEW_FIRST a child of $PREV_LAST"
          git replace --graft "$NEW_FIRST" "$PREV_LAST"
          git filter-repo --replace-refs update-no-add
          echo "=== Diff between $PREV_LAST (prev) and $NEW_FIRST (new) ==="
          git diff "$PREV_LAST" "$NEW_FIRST" || true
      fi

      # Return the last commit SHA for chaining
      echo "$NEW_LAST"
  }

  # Start chain
  echo ">>> Building straight lineage"

  # oldest repo (no previous)
  LAST=$(graft_repo "old1" "$OLD1" "")

  # old2 grafts onto old1
  LAST=$(graft_repo "old2" "$OLD2" "$LAST")

  # old3 grafts onto old2
  LAST=$(graft_repo "old3" "$OLD3" "$LAST")

  # old4 grafts onto old3
  LAST=$(graft_repo "old4" "$OLD4" "$LAST")

  # finally graft current repo onto old4
  FIRST_CURRENT=$(git log main --reverse --format="%H" | head -n 1)
  echo "Grafting current repo first commit $FIRST_CURRENT onto $LAST"
  git replace --graft "$FIRST_CURRENT" "$LAST"
  git filter-repo --replace-refs update-no-add
  git diff "$LAST" "$FIRST_CURRENT" || true

  echo ">>> Done. Full linear history built in $WORKDIR"
  git log --oneline --graph --decorate --all

}