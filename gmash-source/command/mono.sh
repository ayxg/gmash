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

readonly GMASH_MONO_DEFAULT_BRANCH="main"

assert_inside_git_repo(){
  local curr_repo_name_
  curr_repo_name_="$(git_curr_repo)"
  if [ -z "$curr_repo_name_" ]; then
    echo_die "Failed to detect active git repo. You must be inside a git repo."
  fi
  echo "$curr_repo_name_"
}

assert_working_tree_clean(){
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo_die "Working tree is dirty. Please commit or stash changes before proceeding."
  fi
}

# Input arg value cannot be completly unassigned. Empty string "" is considered missing.
assert_required_arg(){
  local _arg_value="$1"
  local _arg_name="$2"
  if [ -z "$_arg_value" ]; then
    echo_die "Missing required '$_arg_name' parameter."
  fi
}

assert_github_api_user(){
  local api_user_
  api_user_="$(gh_api_user)"
  if [ -z "$api_user_" ]; then
    echo_die "Unable to determine GitHub API user. Ensure GitHub CLI (gh) is authenticated."
  fi
  echo "$api_user_"
}

assert_metadata_exists(){
  local _remote="${1:-""}"
  local conf=".gmash/subtree/$_remote.conf"
  if [ ! -f "$conf" ]; then
    echo_die "No subtree metadata found for '$_remote'."
  fi
  echo "$conf"
}

assert_remote_exists(){
  local _remote="${1:-""}"
  if ! git remote get-url "$_remote" &>/dev/null; then
    echo_die "Remote '$_remote' does not exist in this repo."
  fi
}

assert_remote_unused(){
  local _remote="${1:-""}"
  if git config "remote.$_remote.url" > /dev/null; then
    echo_die "Remote '$_remote' already exists."
  fi
}

# Asserts remote url is not already used by any other remotes.
# $1 : Remote url to test.
assert_remote_url_unused(){
  local _url="${1:-""}"
  if git remote -v | awk '{print $2}' | grep -q "^$_url$"; then
    echo_die "URL '$_url' is already used by another remote."
  fi
}

# Asserts path does not exist or is empty.
# $1 : Path to test.
assert_directory_empty_or_nonexistant(){
  local _path="${1:-""}"
  # Guard: prefix path must not exist or be non-empty.
  if [ -e "$_path" ] && [ -n "$(find "$_path" -maxdepth 1 -mindepth 1 -print -quit 2>/dev/null)" ]; then
    echo_die "Target path '$_path' exists and contains files."
  fi
}

# Assert path does not match .gitignore patterns in current repo.
# $1 : Git local path to test.
assert_path_not_gitignored(){
  local _path="${1:-""}"
  if git check-ignore -q "$_prefix"; then
    echo_die "Target path '$_prefix' matches gitignore patterns"
  fi
}

# Assert remote url is accessible
assert_remote_url_accessible(){
  local _url="${1:-""}"
  if ! git ls-remote "$_url" &> /dev/null; then
    echo_die "Provided remote URL '$_url' is not accessible."
  fi
}

# Creates a new remote github repo for a subtree.
create_new_github_repo(){
  local _name="${1:-""}"
  local _owner="${2:-""}"
  assert_github_api_user > /dev/null 2>&1

  if command -v gh >/dev/null 2>&1; then
    if gh repo create "$_owner/$_name" --private --add-readme --description \
      "[gmash] Init subtree repository '$_owner/$_name'" > /dev/null 2>&1; then
      return 0
    else # Unexpected error ?
      echo_die "Failed to create GitHub repository."
    fi
  else # gh not installed...
      echo_die "GitHub CLI (gh) not found. Cannot create new remote repo."
  fi
}

#@doc##########################################################################
  # @func gmash_mono_sub
  # @brief Add subtree to this repo from an existing external git repo,
  #     or create a new remote repo if '--new' is passed. Generates metadata
  #     file at `.gmash/subtree/<remote>.conf` to track the subtree.
#@enddoc#######################################################################
gmash_mono_subtree(){
  #############################################################################
  # Receive input args.
  #############################################################################
  local _prefix="${1:-${GMASH_MONO_SUBTREE_PREFIX:""}}"
  local _remote="${2:-${GMASH_MONO_SUBTREE_REMOTE:""}}"
  local _url="${3:-${GMASH_MONO_SUBTREE_URL:""}}"
  local _branch="${4:-${GMASH_MONO_SUBTREE_BR:-""}}"
  local _squash="${5:-${GMASH_MONO_SUBTREE_SQUASH:-0}}"
  local _new="${6:-${GMASH_MONO_SUBTREE_NEW:-0}}"
  local _name="${7:-${GMASH_MONO_SUBTREE_NAME:-""}}"
  local _owner="${8:-${GMASH_MONO_SUBTREE_OWNER:-""}}"

  #############################################################################
  # Validate input and set defaults
  #############################################################################
  assert_inside_git_repo > /dev/null
  assert_working_tree_clean

  assert_required_arg "$_prefix" "--prefix"
  assert_required_arg "$_remote" "--remote"
  assert_required_arg "$_url" "--url"
  assert_required_arg "$_branch" "--branch"

  assert_remote_unused "$_remote"
  assert_remote_url_unused "$_url"
  assert_directory_empty_or_nonexistant "$_prefix"
  assert_path_not_gitignored "$_prefix"
  assert_remote_url_accessible "$_url"

  # Guard: gmash metadata file must not already exist.
  if [ -f ".gmash/subtree/$_remote.conf" ]; then
    echo_die "Subtree metadata for remote '$_remote' already exists. Try removing first."
  fi

  # Create new github repo if --new flag passed.
  if [ "$_new" -eq "1" ]; then
    vecho_process "Creating new GitHub repo for subtree '$_remote'."
    assert_required_arg "$_name" "--name"
    assert_required_arg "$_owner" "--owner"
    create_new_github_repo "$_name" "$_owner"
    # Set the expected url.
    _url="https://github.com/$_name/$_remote.git"
  fi

  #############################################################################
  # Perfom the subtree operation
  #############################################################################
  vecho_process "Adding subtree '$_remote' from '$_url' into '$_prefix'."
  git remote add -f "$_remote" "$_url"
  git subtree add --prefix="$_prefix" "$_url" "$_branch"

  #############################################################################
  # Add subtree metadata to `.gmash/subtree/$_remote.conf`
  #############################################################################
  vecho_process "Writing subtree metadata to '.gmash/subtree/$_remote.conf'."
  local conf_=".gmash/subtree/$_remote.conf"
  confwrite "$conf_" version "${CONFILE_VERSION}"
  confwrite "$conf_" created "$(date -Iseconds)"
  confwrite "$conf_" url "$_url"
  confwrite "$conf_" remote  "$_remote"
  confwrite "$conf_" branch "$_branch"
  confwrite "$conf_" prefix "$_prefix"
  confwrite "$conf_" squash "$_squash"
  owned_=$(check_repo_access "$_url")
  confwrite "$conf_" owned "$owned_"

  #############################################################################
  # Commit changes.
  #############################################################################
  vecho_process "Committing changes."
  git add "$conf_"
  git commit -m "[gmash] Added subtree '$_remote' at '$_prefix'" \
  -m "
 - url: $_url
 - remote: $_remote
 - prefix: $_prefix
 - metadata: $conf_"

  vecho_done "Success. Subtree '$_remote' added at '$_prefix'."
  return 0
}

#@doc##########################################################################
  # @func gmash_mono_remove
  # @brief Remove subtree remote, prefix and metadata file.
#@enddoc#######################################################################
gmash_mono_remove(){
  #############################################################################
  # Receive input args.
  #############################################################################
  local _remote="${1:-${GMASH_MONO_REMOVE_REMOTE:""}}"
  local _keep_remote="${3:-${GMASH_MONO_REMOVE_KEEP_REMOTE:-0}}"

  #############################################################################
  # Validate input and set defaults
  #############################################################################

  assert_inside_git_repo > /dev/null
  assert_working_tree_clean

  assert_required_arg "$_remote" "--remote"

  local conf_=""
  conf_="$(assert_metadata_exists "$_remote")"

  # Determine prefix from metadata.
  local _prefix=""
  _prefix="$(confread "$conf_" "prefix")"

  if [ -z "$_prefix" ]; then
    echo_die "Failed to read subtree prefix from metadata. Metadata file may be corrupted."
  fi

  #############################################################################
  # Apply removal.
  #############################################################################
  vecho_process "Removing subtree '$_remote' at '$_prefix'"

  # Delete path if it is tracked by Git
  if git ls-files --error-unmatch "$_prefix" >/dev/null 2>&1; then
      vecho_process "Removing tracked subtree '$_prefix' from Git"
      git rm -rf "$_prefix"
  elif [ -d "$_prefix" ]; then
      vecho_process "Path '$_prefix' exists but is untracked. Removing from disk only."
      rm -rf "$_prefix"
  else
      echo_warn "Subtree path '$_prefix' does not exist."
  fi

  # Delete metadata file. Check if the file is tracked by Git
  if git ls-files --error-unmatch "$conf_" >/dev/null 2>&1; then
      git rm -f "$conf_"
  else
      rm "$conf_" # just delete it manually
  fi

  if [[ "$_keep_remote" -eq 0 ]] && git remote get-url "$_remote" &>/dev/null; then
    git remote remove "$_remote"
  fi

  git commit -m "[gmash] Removed subtree '$_remote'" \
             -m "prefix=$_prefix"

  vecho_done "Subtree removed successfully."
}

#@doc##########################################################################
  # @func gmash_mono_pull
  # @brief Pull subtree changes into the monorepo from the subtree remote.
#@enddoc#######################################################################
gmash_mono_pull(){
  #############################################################################
  # Receive input args.
  #############################################################################
  local _remote="${1:-${GMASH_MONO_PULL_REMOTE:""}}"
  local _branch="${2:-${GMASH_MONO_PULL_BRANCH:-""}}"
  local _prefix="${3:-${GMASH_MONO_PULL_PREFIX:""}}"
  local _all="${4:-${GMASH_MONO_PULL_ALL:-0}}"

  #############################################################################
  # Validate input and set defaults
  #############################################################################
  assert_inside_git_repo > /dev/null
  assert_working_tree_clean

  assert_required_arg "$_remote" "--remote"
  assert_remote_exists "$_remote" > /dev/null 2>&1


  # Metadata will be needed if prefix or branch not provided.
  if [ -z "$_prefix" ] || [ -z "$_branch" ]; then
    local conf_=""
    conf_="$(assert_metadata_exists "$_remote")"
  fi

  if [ "$_all" -eq 1 ]; then
    _gmash_mono_pull_all # defer to all-subtrees pull
    return 0
  fi

  # Find metadata if prefix not provided.
  if [ -z "$_prefix" ]; then
    _prefix="$(confread "$conf_" "prefix")"
    if [ -z "$_prefix" ]; then
      echo_die "Failed to read subtree prefix from metadata. Metadata file may be corrupted."
    fi
  fi

  # Find metadata if branch not provided.
  if [ -z "$_branch" ]; then
    _branch="$(confread "$conf_" "branch")"
    if [ -z "$_branch" ]; then
      echo_die "Failed to read subtree branch from metadata. Metadata file may be corrupted."
    fi
  fi

  #############################################################################
  # Apply pull.
  #############################################################################
  git subtree pull --prefix="$_prefix" "$_remote" "$_branch" \
    -m "[gmash mono pull] Pulling updates from '$_remote:$_branch' into '$_prefix'."

  return 0
}

_gmash_mono_pull_all(){
  local gmash_meta_=".gmash/subtree"
  if [ ! -d "$gmash_meta_" ]; then
    echo_die "Subtree metadata directory '$gmash_meta_' not found."
  fi

  for conf_file in "$gmash_meta_"/*.conf; do
    # Glob did not detect any files.
    if [ "$conf_file" == "$gmash_meta_/*.conf" ]; then
      conf_file=""
      echo_die "No subtree metadata found."
    fi

    # Read config values.
    local remote_
    local branch_
    local prefix_
    remote_=$(confread "$conf_file" "remote")
    branch_=$(confread "$conf_file" "branch")
    prefix_=$(confread "$conf_file" "prefix")

    if [ -z "$remote_" ] || [ -z "$branch_" ] || [ -z "$prefix_" ]; then
      vecho_warn "Incomplete metadata in '$conf_file'. Skipping."
      continue
    fi

    vecho_process "Pulling subtree '$remote_' at '$prefix_'."
    if ! gmash_mono_pull \
        "${remote_:-}" \
        "${branch_:-}" \
        "${prefix_:-}"
    then
      echo_err "Failed to pull subtree '$remote_' at '$prefix_'."
      continue
    fi
  done
  return 0
}

gmash_mono_push_cleanup(){
  local _temp_worktree_dir="${1:-""}"
  local _temp_branch="${2:-""}"
  vecho_action "Cleaning up temporary worktree and branch."
  git worktree remove --force "$_temp_worktree_dir" 2>/dev/null || rm -rf "$_temp_worktree_dir"
  git branch -D "$_temp_branch" 2>/dev/null || true
  git worktree prune
}

#@doc##########################################################################
  # @func gmash_mono_push
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
gmash_mono_push(){
  #############################################################################
  # Receive input args.
  #############################################################################
  local _source_branch="${1:-${GMASH_MONO_PUSH_BR:-""}}"
  local _prefix="${2:-${GMASH_MONO_PUSH_PATH:-""}}"
  local _remote="${3:-${GMASH_MONO_PUSH_REMOTE:-""}}"
  local _target_branch="${4:-${GMASH_MONO_PUSH_TGTBR:-""}}"
  local _temp_branch="${7:-${GMASH_MONO_PUSH_TEMPBR:-""}}"
  local _temp_worktree_dir="${8:-${GMASH_MONO_PUSH_TEMPDIR:-""}}"
  local _all="${10:-${GMASH_MONO_PUSH_ALL:-"0"}}"
  local _makepr="${11:-${GMASH_MONO_PUSH_MAKEPR:-"0"}}"
  local _squash="${12:-${GMASH_MONO_PUSH_SQUASH:-"0"}}"

  #############################################################################
  # Validate input and set defaults
  #############################################################################

  # Defer to all-subtrees push if --all passed.
  if [ "$_all" == "1" ]; then
    _gmash_mono_push_all
    return 0
  fi

  assert_inside_git_repo > /dev/null
  assert_working_tree_clean

  assert_required_arg "$_remote" "--remote"
  assert_remote_exists "$_remote"

  local conf_=""
  conf_="$(assert_metadata_exists "$_remote")"

  # Default target branch,prefix,squash from metadata.
  if [ -z "$_target_branch" ]; then
    _target_branch="$(confread "$conf_" "branch")"
    vecho_action "Defaulting target subtree branch($_target_branch) from metadata." 1
  fi

  # Default prefix from metadata.
  if [ -z "$_prefix" ]; then
    _prefix="$(confread "$conf_" "prefix")"
    vecho_action "Defaulting subtree path($_prefix) from metadata." 1
  fi

  # Warn if squash differs from metadata.
  local meta_squash_=""
  meta_squash_="$(confread "$conf_" "squash")"
  if [ "$_squash" != "$meta_squash_" ]; then
    vecho_warn "Warning: squash flag($_squash) differs from metadata($meta_squash_). Forcing to metadata value."
    _squash="$meta_squash_"
  fi

  # If branch or prefix still empty, metadata may be corrupted.
  if [ -z "$_target_branch" ] || [ -z "$_prefix" ]; then
    echo_err "Failed to read subtree metadata from '.gmash/subtree/$_remote.conf'."
    exit 1
  fi

  # Setup squash to be passed to git subtree commands.
  if [ "$_squash" == "1" ]; then
    _squash="--squash"
  else
    _squash=""
  fi

  # Default source branch to current branch.
  if [ -z "$_source_branch" ]; then
    _source_branch="$(git rev-parse --abbrev-ref HEAD)"
    vecho_action "Defaulting mono repo branch($_source_branch) to current branch." 1
  fi

  # Default temporary branch name.
  if [ -z "$_temp_branch" ]; then
    _temp_branch="mono-push-$_remote-$_target_branch-$(date +%s)"
    vecho_action "Defaulting temporary branch($_temp_branch) to '$_remote-update-from-mono'." 1
  fi

  # Default temporary worktree dir.
  if [ -z "$_temp_worktree_dir" ]; then
    _temp_worktree_dir="$(mktemp -d -u --tmpdir "mono-patch-to-$_remote-$_target_branch-XXXXXX")"
    vecho_action "Defaulting temporary worktree dir to '$_temp_worktree_dir'."  1
  fi

  # Does subtree path exist?
  if [ ! -d "$_prefix" ]; then
    echo_die "Subtree path '$_prefix' does not exist."
  fi

  # Is a push even needed?
  git fetch "$_remote" "$_target_branch" 2>/dev/null || true
  if git diff --quiet "HEAD:$_prefix" "$_remote/$_target_branch" -- 2>/dev/null; then
    echo "Already up to date. No subtree changes to push."
    return 0
  fi

  # Add a trap to clean up temp worktree and branch on exit.
  trap "gmash_mono_push_cleanup '$_temp_worktree_dir' '$_temp_branch'" EXIT INT TERM

  # Prepare parent->subtree merge commit message.
  local _merge_msg="[mono:$_prefix -> $_remote] Merged mono push to $_target_branch."

  # Prepare subtree->parent sync commit message.
  local _sync_msg="[mono:$_prefix <- $_remote] Synchronized subtree $_remote:$_target_branch to mono."

  # Attempt to do a fast forward subtree pull->push.
  vecho_process "Running pull from subtree '$_remote:$_target_branch'."
  if output=$(git subtree pull --prefix="$_prefix" "$_remote" "$_target_branch" -m "[gmash mono patch] Accepting updates from subtree." 2>&1 | tee /dev/tty); then
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

  # Begin 3-way sync subtree->parent->subtree.
  vecho_process "Running 3-way sync subtree->parent->subtree."
    git worktree remove --force "$_temp_worktree_dir" 2>/dev/null || rm -rf "$_temp_worktree_dir"
    git branch -D "$_temp_branch" 2>/dev/null || true
    vecho_action "Fetching remote state."
      git fetch "$_remote" "$_target_branch"

    vecho_action "Creating temporary worktree."
      if ! git worktree add --detach "$_temp_worktree_dir" "$_source_branch"; then
        echo_die "Failed to create temporary worktree at '$_temp_worktree_dir'."
      fi

    vecho_action "Moving to worktree directory."
      _original_dir=$(pwd) # Store current directory to return to later
      cd "$_temp_worktree_dir" || echo_die "Failed to change directory to temporary worktree at '$_temp_worktree_dir'."

    vecho_action "Splitting subtree to temporary branch '$_temp_branch'."
      if ! git subtree split --prefix="$_prefix" --branch="$_temp_branch" --rejoin; then
        echo_err "Failed to split subtree to temporary branch '$_temp_branch'. Reversing changes."
        cd "$_original_dir" || echo_die "Failed to return to original directory."
        exit 1
      fi

    vecho_action "Checking out temporary branch '$_temp_branch'."
      if ! git checkout "$_temp_branch"; then
        echo_err "Failed to checkout temporary branch '$_temp_branch'. Reversing changes."
        cd "$_original_dir" || echo_die "Failed to return to original directory."
        exit 1
      fi

    vecho_action "Fetching updates from subtree remote '$_remote'."
      if ! git fetch "$_remote" "$_target_branch"; then
        echo_err "Failed to fetch from subtree remote '$_remote'. Reversing changes."
        cd "$_original_dir" || echo_die "Failed to return to original directory."
        exit 1
      fi

    vecho_action "Checking for common ancestor between mono and subtree."
      if ! git merge-base "$_temp_branch" "$_remote/$_target_branch" >/dev/null 2>&1; then
          vecho_warn "No common ancestor found. Forced to use --allow-unrelated-histories."
          _allow_unrelated="--allow-unrelated-histories"
      else
          _allow_unrelated=""
      fi

    vecho_action "Merging changes to remote subtree."
      if ! git merge "$_remote/$_target_branch" $_allow_unrelated -m "$_merge_msg"; then
          echo_err "Merge failed. Resolve conflicts manually or use --make-pr to create a PR instead."
          cd "$_original_dir" || echo_die "Failed to return to original directory."
          exit 1
      fi

    vecho_action "Pushing to subtree remote."
      if ! git push "$_remote" "$_temp_branch:$_target_branch"; then
          echo_die "Push to subtree remote '$_remote' failed. Resolve conflicts manually or use --make-pr to create a PR instead."
      fi

    vecho_action "Returning to mono and cleaning up."
      cd "$_original_dir" || echo_die "Failed to return to original directory."
      if [ -d "$_temp_worktree_dir" ]; then
          git worktree remove --force "$_temp_worktree_dir" 2>/dev/null || rm -rf "$_temp_worktree_dir"
      fi

      if git show-ref --quiet "refs/heads/$_temp_branch"; then
        git branch -D "$_temp_branch" 2>/dev/null || true
      fi

    vecho_action "Syncing subtree changes back to parent."
      if git fetch "$_remote" "$_target_branch"; then
        if ! git merge -s subtree FETCH_HEAD -m "$_sync_msg"; then
            vecho_warn "Sync-back merge failed. Subtree possibly changed mid-sync."
            return 1
        fi
      else
        vecho_warn "Failed to fetch from remote for sync-back. Unexpected error."
        return 1
      fi

    vecho_action "Validating sync with a mono push."
      if ! git push; then
          echo_err "Final mono push failed. Unexpected error."
          return 1
      fi
  vecho_done "Changes pushed to subtree remote '$_remote' branch '$_target_branch'."
  return 0
}

_gmash_mono_push_all(){
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
    GMASH_MONO_PUSH_REMOTE="$_remote"
    GMASH_MONO_PUSH_URL="$_url"
    GMASH_MONO_PUSH_BR="$_branch"
    GMASH_MONO_PUSH_PATH="$prefix_"
    GMASH_MONO_PUSH_ALL="0" # Disable all to avoid recursion.

    # Store current commit before merge
    local _pre_merge_commit=$(git rev-parse HEAD)

    if gmash_mono_push; then
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

#@doc##########################################################################
  # @func gmash_mono_split
  # @brief Split a prefix folder in the mono repo into a new subtree.
#@enddoc#######################################################################
gmash_mono_split(){
  #############################################################################
  # Receive input args.
  #############################################################################
  local _prefix="${1:-${GMASH_MONO_SPLIT_PREFIX:""}}"
  local _remote="${2:-${GMASH_MONO_SPLIT_REMOTE:""}}"
  local _url="${3:-${GMASH_MONO_SPLIT_URL:""}}"
  local _branch="${4:-${GMASH_MONO_SPLIT_BR:-""}}"
  local _squash="${5:-${GMASH_MONO_SPLIT_SQUASH:-0}}"
  local _new="${6:-${GMASH_MONO_SPLIT_NEW:-0}}"
  local _name="${7:-${GMASH_MONO_SPLIT_NAME:-""}}"
  local _owner="${8:-${GMASH_MONO_SPLIT_OWNER:-""}}"



  #############################################################################
  # Run the subtree splitting operation.
  #############################################################################
  # Generate temporary branch name.
  local temp_branch_=""
  temp_branch_="mono-split-$_remote-$_branch-$(date +%s)"

  # Create new github remote.


  # Split out the prefix into the temp branch.
  git subtree split --prefix="$_prefix" -b "$temp_branch_"

  # Push to the new remote.
  git remote add "$_remote" "https://github.com/$_owner/$_name.git"
  git push "$_remote" "$temp_branch_:$_branch" --force

  # Delete the temporary branch and commit changes.
  git branch -D "$temp_branch_"
  git rm -r my-folder
  git add .
  git commit -m "Remove local folder to replace with subtree"

  # Remove the remote temporarily for the mono subtree call.
  git remote remove "$_remote"

  # Re-establish the subtree link:
  gmash_mono_subtree \
    "${remote_:-}" \
    "${branch_:-}" \
    "${prefix_:-}"
}