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


gmash_mono_patch_all(){
  # Read subtree metadata from .gmash/subtree/*.conf and call mono-patch for each.
  local _subtree_dir=".gmash/subtree"
  if [ ! -d "$_subtree_dir" ]; then
    echo_err "Subtree metadata directory '$_subtree_dir' not found."
    return 1
  fi

  vecho_process "Scanning subtree metadata directory '$_subtree_dir' for subtrees to patch."
  local _patched_any=0
  local _merge_commits=()
  local _starting_commit=$(git rev-parse HEAD)

  for conf_file in "$_subtree_dir"/*.conf; do
    if [ "$conf_file" == "$_subtree_dir/*.conf" ]; then
      conf_file=""
      break
    fi

    if [ ! -f "$conf_file" ]; then
      vecho_action "No subtree metadata files found in '$_subtree_dir'."
      vecho_action "Skipping mono-patch-all."
      break
    fi
    vecho_action "Processing subtree metadata file '$conf_file'."
    # Read config values.
    local _url
    local _remote
    local _branch
    local prefix_
    local _squash
    local _owned
    _url=$(confread "$conf_file" "url")
    _remote=$(confread "$conf_file" "remote")
    _branch=$(confread "$conf_file" "branch")
    prefix_=$(confread "$conf_file" "prefix")
    _squash=$(confread "$conf_file" "squash")
    _owned=$(confread "$conf_file" "owned")

    if [ -z "$_remote" ] || [ -z "$_url" ] || [ -z "$_branch" ] || [ -z "$prefix_" ]; then
      vecho_warn "Incomplete metadata in '$conf_file'. Skipping."
      continue
    fi

    vecho_process "Patching subtree '$_remote' at '$prefix_' from '$_url'."
    GMASH_MONO_PATCH_REMOTE="$_remote"
    GMASH_MONO_PATCH_URL="$_url"
    GMASH_MONO_PATCH_BR="$_branch"
    GMASH_MONO_PATCH_PATH="$prefix_"
    GMASH_MONO_PATCH_ALL="0" # Disable all to avoid recursion.

    # Store current commit before merge
    local _pre_merge_commit=$(git rev-parse HEAD)

    if gmash_mono_patch; then
      # Capture the merge commit hash if a new commit was created
      local _post_merge_commit=$(git rev-parse HEAD)
      if [ "$_pre_merge_commit" != "$_post_merge_commit" ]; then
        _merge_commits+=("$_post_merge_commit")
        vecho_done "Successfully patched subtree '$_remote'. Merge commit: ${_post_merge_commit:0:8}"
      else
        vecho_done "No changes for subtree '$_remote' (already up to date)."
      fi
      _patched_any=1
    else
      vecho_warn "Failed to patch subtree '$_remote'. Continuing to next."
    fi
  done

  if [ $_patched_any -eq 0 ]; then
    vecho_warn "No subtrees were patched. Either no metadata files found or all patches failed."
  else
    vecho_done "Mono patched with all applicable subtrees."
  fi

  return 0
}

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
  local _br=${GMASH_MONO_PATCH_BR:-'main'}
  local _path=${GMASH_MONO_PATCH_PATH:-'subtreeDirName'}
  local _remote=${GMASH_MONO_PATCH_REMOTE:-'origin'}
  local _tgtbr=${GMASH_MONO_PATCH_TGTBR:-'main'}
  local _user=${GMASH_MONO_PATCH_USER:-{currentGithubUser}}
  local _tgtuser=${GMASH_MONO_PATCH_TGTUSER:-$_user}
  local _tempbr=${GMASH_MONO_PATCH_TEMPBR:-""}
  local _tempdir=${GMASH_MONO_PATCH_TEMPDIR:-""}
  local _url=${GMASH_MONO_PATCH_URL:-""}

  local _all=${GMASH_MONO_PATCH_ALL:-"0"}
  local _makepr=${GMASH_MONO_PATCH_MAKEPR:-"0"}
  local _squash=${GMASH_MONO_PATCH_SQUASH-"0"}

  local _curr_repo_name=$(basename $(git rev-parse --show-toplevel))
  vecho_process "Applying patch from mono : $_user/$_curr_repo_name"

  if [ "$_all" == "1" ]; then
    vecho_process "Scanning repo for subtree metadata in '.gmash/subtrees'."
    gmash_mono_patch_all
    return 0
  fi

  vecho_process "Verifying parameters"
    if [ -z "$_user" ]; then
      echo_err "Must specify a github user/org to own the mono repo with --user or -u."
      return 1
    fi

    if [ -z "$_remote" ] && [ "$_all" != "1" ]; then
      echo_err "Must specify a subtree remote alias with --remote or use --all to patch all subtrees."
      return 1
    fi

    if [ -z "${_name:-}" ]; then
      _name="$_remote"
      vecho_action "Defaulting subtree name($_name) to remote alias($_remote)." 1
    fi

    if [ -z "$_tgtuser" ]; then
      _tgtuser="$_user"
      vecho_action "Defaulting target user($_tgtuser) to source user($_user)." 1
    fi

    if [ -z "$_br" ]; then
      _br="main"
      vecho_action "Defaulting mono repo branch($_br) to 'main'." 1
    fi

    if [ -z "$_tgtbr" ]; then
      _tgtbr="main"
      vecho_action "Defaulting target subtree branch($_tgtbr) to 'main'." 1
    fi

    if [ -z "$_path" ]; then
      _path="projects/$_name"
      vecho_action "Defaulting subtree path($_path) to 'projects/$_name'." 1
    fi

    if [ -z "$_tempbr" ]; then
      _tempbr="mono-patch-to-$_remote-$_tgtbr"
      vecho_action "Defaulting temporary branch($_tempbr) to '$_remote-update-from-mono'." 1
    fi

    if [ -z "$_tempdir" ]; then
      _tempdir="../mono-patch-sync-temp-$_remote-$_tgtbr"
      vecho_action "Defaulting temporary worktree dir to '../mono-patch-sync-temp-$_remote-$_tgtbr'."  1
    fi

    # Negative tests.
    local _correct_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$_correct_branch" != "$_br" ]; then
      echo_err "Must be on $_br branch (currently on $_correct_branch)."
      return 1
    fi

    if [ -z "$_remote" ] && [ "$_all" != "1" ]; then
      echo_err "Must specify a subtree remote alias with --remote or use --all to patch all subtrees."
      return 1
    fi

    if ! git remote get-url "$_remote" >/dev/null 2>&1; then
      echo_err "Subtree remote '$_remote' not found."
      return 1
    fi

    if [ -z "$_url" ]; then
      _url=$(git remote get-url "$_remote" 2>/dev/null)
      if [ $? -ne 0 ]; then
        echo_err "Could not determine URL of subtree remote '$_remote'. Please specify with --url."
        return 1
      fi
      vecho_action "Fetched URL($_url) from existing remote alias($_remote)." 1
    fi

    if [ ! -d "$_path" ]; then
      echo_err "Subtree path '$_path' does not exist."
      return 1
    fi
    # Set url.
    _url=$(git remote get-url "$_remote") # Will overwrite if already correct since remote must match URL.
  vecho_done "Params verified, working on mono branch '$_user/$_curr_repo_name:$_br' at '$_url'."

  # Attempt to do a fast forward subtree pull->push.
  vecho_process "Running fast-forward push to subtree '$_remote:$_tgtbr'."
  if output=$(git subtree pull --prefix="$_path" "$_remote" "$_tgtbr" -m "[gmash mono patch] Accepting updates from subtree." 2>&1 | tee /dev/tty); then
    if echo "$output" | grep -q "Already up to date"; then
      vecho_action "No new subtree changes detected."

    else
      vecho_action "Accepted new subtree changes, pushing subtree updates to remote mono."
      git pull
      git push
    fi
  else
      echo_err "Failed to pull subtree remote. Remote possibly corrupted."
      exit 1
  fi

  vecho_process "Checking if subtree sync is needed..."
    git fetch "$_remote" "$_tgtbr" 2>/dev/null || true
    if git diff --quiet "HEAD:$_path" "$_remote/$_tgtbr" -- 2>/dev/null; then
      # exit early here.
      return 0
    else
      vecho_warn "Subtree content differs, 3 way sync required."
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
  vecho_process "Running 3-way sync subtree->parent->subtree."
    git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
    git branch -D "$_tempbr" 2>/dev/null || true
    vecho_action "Fetching remote state."
      vecho_func "git fetch '$_remote' '$_tgtbr'"
      git fetch "$_remote" "$_tgtbr"

    vecho_action "Creating temporary worktree."
      vecho_func "git worktree add --detach '$_tempdir' '$_br'"
      if ! git worktree add --detach "$_tempdir" "$_br"; then
        echo_err "Failed to create temporary worktree at '$_tempdir'."
      exit 1
      fi

    vecho_action "Moving to worktree directory."
      _original_dir=$(pwd) # Store current directory to return to later
      cd "$_tempdir" # Move to worktree directory

    vecho_action "Splitting subtree to temporary branch '$_tempbr'."
      vecho_func "git subtree split --prefix='$_path' --branch='$_tempbr'"
      if ! git subtree split --prefix="$_path" --branch="$_tempbr"; then
        echo_err "Failed to split subtree to temporary branch '$_tempbr'. Reversing changes."
        cd "$_original_dir"
        git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
        return 1
      fi

    vecho_action "Checking out temporary branch '$_tempbr'."
      vecho_func "git checkout '$_tempbr'"
      if ! git checkout "$_tempbr"; then
        echo_err "Failed to checkout temporary branch '$_tempbr'. Reversing changes."
        cd "$_original_dir"
        git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
        git branch -D "$_tempbr" 2>/dev/null || true
        return 1
      fi

    vecho_action "Fetching updates from subtree remote '$_remote'."
      vecho_func "git fetch '$_remote' '$_tgtbr'"
      if ! git fetch "$_remote" "$_tgtbr"; then
        echo_err "Failed to fetch from subtree remote '$_remote'. Reversing changes."
        cd "$_original_dir"
        git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
        git branch -D "$_tempbr" 2>/dev/null || true
        return 1
      fi

    vecho_action "Merging changes to remote subtree."
      vecho_func "git merge '$_remote/$_tgtbr' --allow-unrelated-histories -m 'Merge parent changes to remote subtree'"
      if ! git merge "$_remote/$_tgtbr" --allow-unrelated-histories -m "$_merge_msg"; then
          echo_err "Merge failed. Resolve conflicts manually or use --make-pr to create a PR instead."
          cd "$_original_dir"
          git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
          git branch -D "$_tempbr" 2>/dev/null || true
          exit 1
      fi

    vecho_action "Pushing to subtree remote."
      vecho_func "git push '$_remote' '$_tempbr:$_tgtbr'"
      if ! git push "$_remote" "$_tempbr:$_tgtbr"; then
          echo_err "Push to subtree remote '$_remote' failed. Resolve conflicts manually or use --make-pr to create a PR instead."
          exit 1
      fi

    vecho_action "Returning to mono and cleaning up."
      cd "$_original_dir"
      vecho_func "git worktree remove --force '$_tempdir'"
      if [ -d "$_tempdir" ]; then
          git worktree remove --force "$_tempdir" 2>/dev/null || rm -rf "$_tempdir"
      fi

      vecho_func "git branch -D '$_tempbr'"
      if git show-ref --quiet "refs/heads/$_tempbr"; then
        git branch -D "$_tempbr" 2>/dev/null || true
      fi

    vecho_action "Syncing subtree changes back to parent."
      vecho_func "git fetch '$_remote' '$_tgtbr'"
      if git fetch "$_remote" "$_tgtbr"; then
        vecho_func "git merge -s subtree FETCH_HEAD -m ..."
        if ! git merge -s subtree FETCH_HEAD -m "$_sync_msg"; then
            vecho_warn "Sync-back merge failed. Subtree possibly changed mid-sync."
            return 1
        fi
      else
        vecho_warn "Failed to fetch from remote for sync-back. Unexpected error."
        return 1
      fi

    vecho_action "Validating sync with a mono push."
      vecho_func "git push"
      if ! git push; then
          echo_err "Final mono push failed. Unexpected error."
          return 1
      fi
  vecho_done "3 Way sync complete, changes pushed to subtree remote '$_remote' branch '$_tgtbr'."
  vecho_done "Mono patched applied."

  return 0
}


# Clone monorepo from github. Add all subtrees from metadata.
gmash_mono_clone(){
  local _user="$GMASH_MONO_CLONE_USER"
  local _dir="$GMASH_MONO_CLONE_DIR"
  local _br="$GMASH_MONO_CLONE_BR"

  if [ -z "$_user" ]; then
    echo_err "Must specify a github user/org to own the mono repo with --user or -u."
    return 1
  fi

  if [ -z "$_dir" ]; then
    _dir="$_user-mono-repo"
    vecho_action "Defaulting mono clone directory($_dir) to '$_user-mono-repo'."
  fi

  if [ -z "$_br" ]; then
    _br="main"
    vecho_action "Defaulting mono repo branch($_br) to 'main'."
  fi

  vecho_info "Input parameters:"
  vecho_info "- user:   $_user"
  vecho_info "- dir:    $_dir"
  vecho_info "- br:     $br"

  if [ -d "$_dir" ]; then
    echo_err "Target directory '$_dir' already exists. Please remove or choose another with --dir."
    return 1
  fi

  vecho_process "Cloning mono repo from '$_user/$_user-mono-repo' into '$_dir'."
    if ! git clone "$_user/$_user-mono-repo" "$_dir"; then
      echo_err "Failed to clone mono repo from '$_user/$_user-mono-repo'. Ensure the repo exists and you have access."
      return 1
    fi
    cd "$_dir" || return 1
    if ! git checkout "$_br"; then
      echo_err "Branch '$_br' does not exist in the mono repo."
      return 1
    fi
  vecho_done "Successfully cloned mono repo."


  vecho_process "Adding subtrees from metadata."
  for conf_file in ../.gmash/subtree/*.conf; do
    if [ "$conf_file" == "../.gmash/subtree/*.conf" ]; then
      # No .conf files found, break the loop.
      conf_file=""
      break
    fi

    if [ ! -f "$conf_file" ]; then
      vecho_action "No subtree metadata files found in '../.gmash/subtree'. Skipping mono-clone subtree addition."
      break
    fi
    vecho_action "Processing subtree metadata file '$conf_file'."
    # Read config values.
    local _url
    local _remote
    local _branch
    local _path
    local _squash
    local _owned
    _url=$(confread "$conf_file" "url")
    _remote=$(confread "$conf_file" "remote")
    _branch=$(confread "$conf_file" "branch")
    _path=$(confread "$conf_file" "path")
    _squash=$(confread "$conf_file" "squash")
    _owned=$(confread "$conf_file" "owned")

    if [ -z "$_remote" ] || [ -z "$_url" ] || [ -z "$_branch" ] || [ -z "$_path" ]; then
      echo_err "Incomplete metadata in '$conf_file'. Skipping."
      continue
    fi

    vecho_action "Adding subtree '$_remote' at '$_path' from '$_url'."
    git remote add "$_remote" "$_url"

  done

  vecho_done "Successfully added all subtrees from metadata."
}