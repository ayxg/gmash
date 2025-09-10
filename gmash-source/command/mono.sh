#!/bin/bash
#@doc##########################################################################
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
###############################################################################
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
# @created: 2025/08/31
###############################################################################
# @file gmash->mono command group
#@enddoc#######################################################################

#@doc##########################################################################
# @func gmash_mono_patch
# @brief Push commits made in a monorepo to an owned subtree repo.
#
# Attempt to push subtree changes from mono to subtree by fast forward method.
# If fast forward fails, 3-way sync subtree->parent->subtree. Changes from the
# parent repo are forced to a temp copy of the current subtree repo then merged
# into the parent to resolve conflicts. Once merged to parent, changes are
# synced back to the subtree repo(no change occurs unless conflicts occured
# during sync-back). If fast-forward conflicts cannot be auto-resolved:
#   ? --makepr  -> a fork->pull-request is made instead of pushing directly
#                 to the subtree repo.
#     else      -> error and the user must resolve conflicts manually.
#
# @warning Commit changes to mono before calling mono-patch.
#
# The implementation.
# Use case : make change in local parent. Push changes to child.
#
# First, lets overview the advertised api of git subtree.
# For example, given a subtree remote called 'foo' targeting branch 'main'.
#
# In theory this ideal set of commands would make sense. But actually it fails.
# We just pulled. Yet we are behind? Why?
# TODO: answer why when I finnaly understand why.
# git push
#   > Everything up-to-date
# git pull -s subtree foo main
#   > * branch            main       -> FETCH_HEAD
#   > Already up to date.
# git subtree push --prefix=projects/foo foo main
#   > git push using:  foo main
#   > To https://github.com/SophiaSGS/subtree4.git
#   >  ! [rejected] 22d7ddf39497f539ebdd3faef42f735868059c60 -> main (non-fast-forward)
#   > error: failed to push some refs to 'https://github.com/SophiaSGS/foo.git'
#   > hint: Updates were rejected because the tip of your current branch is behind
#   > hint: its remote counterpart. If you want to integrate the remote changes,
#   > hint: use 'git pull' before pushing again.
#   > hint: See the 'Note about fast-forwards' in 'git push --help' for details.
#
# Another 'option' is to simply --force the parent changes onto the subtree.
# But this clearly isn't what we need. This set of commands will erase all
# previous commit history of the subtree ,and overwrite with the parent commits
# for that subtree.
#   git subtree split --prefix=projects/foo --branch=foo-temp
#   git push foo foo-temp:main --force
#   git branch -D foo-temp
#   git subtree push --prefix=projects/foo foo main
#
# And finnaly, I present my 3-way sync push. This seems to be the best method
# that I have figured out through brute force testing. Information on the
# internet regarding pushing from the parent to child is severely lacking.
# Overview :
#   1. Commit changes to parent.
#   2. Split temp branch from subtree and merge back onto parent.
#   3. Resolve conficts, if any.
#   4. Fetch and merge the updated subtree.
#
# Its definitley slow - but it gets the job done. Overall, from gathered
# info people reccomend either :
#   - Using subtrees as view-only from the parent perspective.
#   - To avoid subtree push unless necessary.
# !!(actually after some testing it seems about as-fast as a subtree push...)
#
# In Detail:
#   0. Open git-bash in your root parent repo path.
#
#   1. Commit changes in git-bash and add each changed file manually,
#      or directly in Visual Studio which will automate this process.
#     git add "projects/foo/new_file2"
#     git commit -a -m "Modifiaction" -m "details"
#     git push
#
#   2. Create a temp branch from subtree, then merge into main parent
#      branch to resolve possible conflicts.
#     git subtree split --prefix=projects/foo --branch=foo-update-from-mono
#     git checkout foo-update-from-mono
#     git merge foo/main --allow-unrelated-histories -m ...
#     git push foo foo-update-from-mono:main
#     git checkout main
#     git branch -D foo-update-from-mono
#
#   3. At this point, the subtree child repo is synced with the parent.
#      Last step, is to sync the updated commits from the child,by merging
#      them back up to the parent repo.
#     git fetch foo main
#     git merge -s subtree FETCH_HEAD -m ...
#     git push
#
# @note you may get some debug info about the current subtree beforehand
#       to assert there are no conflicts...
#   git fetch foo
#   git log foo/main --oneline
#
# @warning METHOD below is a fake news. subtree does NOT have a push/pull-all
#          command.
# @note !BAD REFERENCE! Ref:
#       https://opensource.com/article/20/5/git-submodules-subtrees
#@enddoc#######################################################################
gmash_mono_patch(){
  local _br="$GMashParamBr"
  local _path="$GMashParamPath"
  local _remote="$GMashParamRemote"
  local _tgtbr="$GMashParamTgtBr"
  local _tgtuser="$GMashParamTgtUser"
  local _tempbr="$GMashFlagTempBr"
  local _tempdir="$GMashFlagTempDir"
  local _user="$GMashParamUser"
  local _url="$GMashParamUrl"

  local _all="$GMashFlagAll"
  local _makepr="$GMashFlagMakePr"
  local _squash="$GMashFlagSquash"

  local _curr_repo_name=$(basename $(git rev-parse --show-toplevel))

  gmash_verb "\e[33;1m[$_user/$_curr_repo_name][gmash->mono-patch]\e[0m
      \e[34m\tⓘ Input arguments:\e[0m
      \t\t[--br] '$_br',
      \t\t[--path] '$_path',
      \t\t[--remote] '$_remote',
      \t\t[--tgtbr] '$_tgtbr',
      \t\t[--tgtuser] '$_tgtuser',
      \t\t[--tempbr] '$_tempbr',
      \t\t[--tempdir] '$_tempdir',
      \t\t[--user] '$_user',
      \t\t[--url] '$_url',
      \t\t[--all] '$_all',
      \t\t[--make-pr] '$_makepr',
      \t\t[--squash] '$_squash'"

  # Verify git state & parameters.
  gmash_verb "\e[35m\t⚙ Verifying parameters.\e[0m"
    if [ -z "$_user" ]; then
      echo "[gmash][mono-patch][error]: Must specify a github user/org to own the mono repo with --user or -u."
      return 1
    fi
    if [ -z "$_remote" ] && [ "$_all" != "1" ]; then
      echo "[gmash][mono-patch][error]: Must specify a subtree remote alias with --remote or use --all to patch all subtrees."
      return 1
    fi
    if [ -z "$_name" ]; then
      _name="$_remote"
      gmash_verb "\t\t-> Defaulting subtree name($_name) to remote alias($_remote)."
    fi
    if [ -z "$_tgtuser" ]; then
      _tgtuser="$_user"
      gmash_verb "\t\t-> Defaulting target user($_tgtuser) to source user($_user)."
    fi
    if [ -z "$_br" ]; then
      _br="main"
      gmash_verb "\t\t-> Defaulting mono repo branch($_br) to 'main'."
    fi
    if [ -z "$_tgtbr" ]; then
      _tgtbr="main"
      gmash_verb "\t\t-> Defaulting target subtree branch($_tgtbr) to 'main'."
    fi
    if [ -z "$_path" ]; then
      _path="projects/$_name"
      gmash_verb "\t\t-> Defaulting subtree path($_path) to 'projects/$_name'."
    fi
    if [ -z "$_tempbr" ]; then
      _tempbr="mono-patch-to-$_remote-$_tgtbr"
      gmash_verb "\t\t-> Defaulting temporary branch($_tempbr) to '$_remote-update-from-mono'."
    fi
    if [ -z "$_tempdir" ]; then
      _tempdir="../mono-patch-sync-temp-$_remote-$_tgtbr"
      gmash_verb "\t\t-> Defaulting temporary worktree dir to '../mono-patch-sync-temp-$_remote-$_tgtbr'."
    fi

    # Negative tests.
    local _correct_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$_correct_branch" != "$_br" ]; then
      echo "[gmash][new-subtree][error]: Must be on $_br branch (currently on $_correct_branch)."
      return 1
    fi
    if [ -z "$_remote" ] && [ "$_all" != "1" ]; then
      echo "[gmash][mono-patch][error]: Must specify a subtree remote alias with --remote or use --all to patch all subtrees."
      return 1
    fi
    if ! git remote get-url "$_remote" >/dev/null 2>&1; then
      echo "[gmash][mono-patch][error]: Subtree remote '$_remote' not found."
      return 1
    fi
    if [ -z "$_url" ]; then
      _url=$(git remote get-url "$_remote" 2>/dev/null)
      if [ $? -ne 0 ]; then
        echo "[gmash][mono-patch][error]: Could not determine URL of subtree remote '$_remote'. Please specify with --url."
        return 1
      fi
      gmash_verb "\t\t-> Fetched URL($_url) from existing remote alias($_remote)."
    fi
    if [ ! -d "$_path" ]; then
      echo "[gmash][mono-patch][error]: Subtree path '$_path' does not exist."
      return 1
    fi
    # Set url.
    _url=$(git remote get-url "$_remote") # Will overwrite if already correct since remote must match URL.
  gmash_verb "\e[32m\t  ✓ Params verified, working on mono branch '$_user/$_curr_repo_name:$_br' at '$_url'.\e[0m"

  gmash_verb "\e[34m\tⓘ Final input arguments:\e[0m
  \t\t[--br] '$_br',
  \t\t[--path] '$_path',
  \t\t[--remote] '$_remote',
  \t\t[--tgtbr] '$_tgtbr',
  \t\t[--tgtuser] '$_tgtuser',
  \t\t[--tempbr] '$_tempbr',
  \t\t[--tempdir] '$_tempdir',
  \t\t[--url] '$_url',
  \t\t[--user] '$_user',
  \t\t[--all] '$_all',
  \t\t[--make-pr] '$_makepr',
  \t\t[--squash] '$_squash'"

  # Attempt to do a fast forward subtree pull->push.
  gmash_verb "\e[35m\t⚙ Running fast-forward push to subtree '$_remote:$_tgtbr'.\e[0m"
  if output=$(git subtree pull --prefix="$_path" "$_remote" "$_tgtbr" -m "[gmash][mono-patch] Accepting updates from subtree." 2>&1 | tee /dev/tty); then
    if echo "$output" | grep -q "Already up to date"; then
      gmash_verb "\t\t-> No new subtree changes detected."

    else
      gmash_verb "\t\t-> Accepted new subtree changes, pushing subtree updates to remote mono."
      git pull
      git push
    fi
  else
      echo "[gmash][mono-patch][fatal]: Failed to pull subtree remote. Remote possibly corrupted."
      exit 1
  fi

  gmash_verb "\e[35m\t⚙ Checking if subtree sync is needed...\e[0m"
    git fetch "$_remote" "$_tgtbr" 2>/dev/null || true
    if git diff --quiet "HEAD:$_path" "$_remote/$_tgtbr" -- 2>/dev/null; then
      # exit early here.
      gmash_verb "\t\t-> Subtree content is synced"
      gmash_verb "\e[32m\t  ✓ Success. Mono is patched.\e[0m"
      gmash_verb "\e[34m\t[gmash][mono-patch] ⓘ Result metadata:\e[0m
      \t\t[--br] '$_br',
      \t\t[--path] '$_path',
      \t\t[--remote] '$_remote',
      \t\t[--tgtbr] '$_tgtbr',
      \t\t[--tgtuser] '$_tgtuser',
      \t\t[--tempbr] '$_tempbr',
      \t\t[--tempdir] '$_tempdir',
      \t\t[--url] '$_url',
      \t\t[--all] '$_all',
      \t\t[--make-pr] '$_makepr',
      \t\t[--squash] '$_squash'"
      return 0
    else
      gmash_verb "\t\t-> Subtree content differs, 3 way sync required."
    fi

  # Prepare parent->subtree merge commit message.
  local _merge_msg="[mono:$_path -> $_remote] Merge mono patch to $_tgtbr.
      [--br] '$_br',
      [--path] '$_path',
      [--remote] '$_remote',
      [--tgtbr] '$_tgtbr',
      [--tgtuser] '$_tgtuser',
      [--tempbr] '$_tempbr',
      [--tempdir] '$_tempdir',
      [--url] '$_url',
      [--all] '$_all',
      [--make-pr] '$_makepr',
      [--squash] '$_squash'"

  # Prepare subtree->parent sync commit message.
  local _sync_msg="[mono:$_path <- $_remote] Synchronized child subtree $_remote:$_tgtbr to mono.
      [--br] '$_br',
      [--path] '$_path',
      [--remote] '$_remote',
      [--tgtbr] '$_tgtbr',
      [--tgtuser] '$_tgtuser',
      [--tempbr] '$_tempbr',
      [--tempdir] '$_tempdir',
      [--url] '$_url',
      [--all] '$_all',
      [--make-pr] '$_makepr',
      [--squash] '$_squash'"


  # Begin 3-way sync subtree->parent->subtree.
  gmash_verb "\e[35m\t⚙ Running 3-way sync subtree->parent->subtree.\e[0m"
    git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
    git branch -D "$_tempbr" 2>/dev/null || true
    gmash_verb "\t\t-> Fetching remote state."
      gmash_verb "\e[33m\t💻 git fetch '$_remote' '$_tgtbr'"
      git fetch "$_remote" "$_tgtbr"

    gmash_verb "\t\t-> Creating temporary worktree."
      gmash_verb "\e[33m\t💻 git worktree add --detach '$_tempdir' '$_br'"
      if ! git worktree add --detach "$_tempdir" "$_br"; then
        echo "[gmash][mono-patch][error]: Failed to create temporary worktree at '$_tempdir'."
      exit 1
      fi

    gmash_verb "\t\t-> Moving to worktree directory."
      _original_dir=$(pwd) # Store current directory to return to later
      cd "$_tempdir" # Move to worktree directory

    gmash_verb "\t\t-> Splitting subtree to temporary branch '$_tempbr'."
      gmash_verb "\e[33m\t💻 git subtree split --prefix='$_path' --branch='$_tempbr'"
      if ! git subtree split --prefix="$_path" --branch="$_tempbr"; then
        echo "[gmash][mono-patch][error]: Failed to split subtree to temporary branch '$_tempbr'. Reversing changes."
        cd "$_original_dir"
        git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
        return 1
      fi

    gmash_verb "\t\t-> Checking out temporary branch '$_tempbr'."
      gmash_verb "\e[33m\t💻 git checkout '$_tempbr'"
      if ! git checkout "$_tempbr"; then
        echo "[gmash][mono-patch][error]: Failed to checkout temporary branch '$_tempbr'. Reversing changes."
        cd "$_original_dir"
        git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
        git branch -D "$_tempbr" 2>/dev/null || true
        return 1
      fi

    gmash_verb "\t\t-> Fetching updates from subtree remote '$_remote'."
      gmash_verb "\e[33m\t💻 git fetch '$_remote' '$_tgtbr'"
      if ! git fetch "$_remote" "$_tgtbr"; then
        echo "[gmash][mono-patch][error]: Failed to fetch from subtree remote '$_remote'. Reversing changes."
        cd "$_original_dir"
        git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
        git branch -D "$_tempbr" 2>/dev/null || true
        return 1
      fi

    gmash_verb "\t\t-> Merging changes to remote subtree."
      gmash_verb "\e[33m\t💻 git merge '$_remote/$_tgtbr' --allow-unrelated-histories -m 'Merge parent changes to remote subtree'"
      if ! git merge "$_remote/$_tgtbr" --allow-unrelated-histories -m "$_merge_msg"; then
          echo "[gmash][mono-patch][error]: Merge failed. Resolve conflicts manually or use --make-pr to create a PR instead."
          cd "$_original_dir"
          git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
          git branch -D "$_tempbr" 2>/dev/null || true
          exit 1
      fi

    gmash_verb "\t\t-> Pushing to subtree remote."
      gmash_verb "\e[33m\t💻 git push '$_remote' '$_tempbr:$_tgtbr'"
      if ! git push "$_remote" "$_tempbr:$_tgtbr"; then
          echo "[gmash][mono-patch][error]: Push to subtree remote '$_remote' failed. Resolve conflicts manually or use --make-pr to create a PR instead."
          exit 1
      fi

    gmash_verb "\t\t-> Returning to mono and cleaning up."
      cd "$_original_dir"
      gmash_verb "\e[33m\t💻 git worktree remove --force '$_tempdir'"
      if [ -d "$_tempdir" ]; then
          git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
      fi

      gmash_verb "\e[33m\t💻 git branch -D '$_tempbr'"
      if git show-ref --quiet "refs/heads/$_tempbr"; then
        git branch -D "$_tempbr" 2>/dev/null || true
      fi

    gmash_verb "\t\t-> Syncing subtree changes back to parent."
      gmash_verb "\e[33m\t💻 git fetch '$_remote' '$_tgtbr'"
      if git fetch "$_remote" "$_tgtbr"; then
        gmash_verb "\e[33m\t💻 git merge -s subtree FETCH_HEAD -m ..."
        if ! git merge -s subtree FETCH_HEAD -m "$_sync_msg"; then
            echo "[gmash][mono-patch][fatal]: Sync-back merge failed. Subtree possibly changed mid-sync."
            return 1
        fi
      else
        echo "[gmash][mono-patch][fatal]: Failed to fetch from remote for sync-back. Unexpected error."
        return 1
      fi

    gmash_verb "\t\t -> Validating sync with a mono push."
      gmash_verb "\e[33m\t💻 git push"
      if ! git push; then
          echo "[gmash][mono-patch][error]: Final mono push failed. Unexpected error."
          return 1
      fi
  gmash_verb "\e[32m\t  ✓ 3 Way sync complete, changes pushed to subtree remote '$_remote' branch '$_tgtbr'.\e[0m"

  gmash_verb "\e[32m\t  ✓ Success. Mono is patched.\e[0m"
  gmash_verb "\e[34m\t[gmash][mono-patch] ⓘ Result metadata:\e[0m
    \t\t[--br] '$_br',
    \t\t[--path] '$_path',
    \t\t[--remote] '$_remote',
    \t\t[--tgtbr] '$_tgtbr',
    \t\t[--tgtuser] '$_tgtuser',
    \t\t[--tempbr] '$_tempbr',
    \t\t[--tempdir] '$_tempdir',
    \t\t[--url] '$_url',
    \t\t[--all] '$_all',
    \t\t[--make-pr] '$_makepr',
    \t\t[--squash] '$_squash'"
}