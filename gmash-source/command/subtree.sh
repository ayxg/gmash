#!/bin/bash
#@doc##########################################################################
  # SPDX-License-Identifier: AGPL-3.0-or-later
  # Copyright(c) 2025 Anton Yashchenko
  #############################################################################
  # @project: [gmash] Git Smash
  # @author(s): Anton Yashchenko
  # @website: https://www.acpp.dev
  #############################################################################
  # @file gmash->subtree command group
  # @created: 2025/08/31
  #
  # Detailed overview of the git process for creating an example subtree 'foo-box'.
  # For each submodule:
  # 1. Create github repo with only a single commit (eg. .gitignore or README.md).
  #
  # 2. Create a folder for the submodule inside the monorepo submodules directory.
  #
  # 3. Set up the monorepo for a subtree merge.
  #   1. Open "git-bash" console in the local monorepo folder.
  #
  #   2. Add a new remote URL pointing to the separate submodule repo that was
  #      created on step 1.
  #     git remote add -f foo-box https://github.com/SophiaSGS/foo-box.git
  #     Updating foo-box
  #     remote: Enumerating objects: 3, done.
  #     remote: Counting objects: 100% (3/3), done.
  #     remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
  #     Unpacking objects: 100% (3/3), 869 bytes | 8.00 KiB/s, done.
  #     From https://github.com/SophiaSGS/foo-box
  #     * [new branch]      main       -> foo-box/main
  #
  #   3. Merge the submodule repo into the monorepo. This doesn't change any of
  #      your files locally, but it does prepare Git for the next step.
  #      You must also indicate which specific branch you wish to merge. In this
  #      case 'main'.
  #         git merge -s ours --no-commit --allow-unrelated-histories foo-box/main
  #      Automatic merge went well; stopped before committing as requested
  #
  #   4. Create a folder for the submodule inside the monorepo submodules directory.
  #      Then, copy the Git history of the submodule project into it using
  #      'read-tree'. '--prefix' is the path inside the monorepo where the module
  #      will be stored. You must also specify the branch argument '-u'.
  #           "Not a fatal error? false positive."
  #         git read-tree --prefix=boxes/foo_box/ -u foo-box/main
  #         fatal: refusing to merge unrelated histories
  #
  #   5. Commit the submodule subtree changes locally.
  #     git commit -m "Merged submodule subtree 'foo-box' into monorepo 'boxes/foo_box'."
  #     [main fe0ca25] Merged submodule subtree 'foo-box' into monorepo 'boxes/foo_box'.
  #
  #   6. Push the monorepo's submodule tree changes to the remote GitHub monorepo
  #      from the git-bash.
  #       git push
#@enddoc#######################################################################

# @brief Patch subtree from its remote repo.
# $1 = remote
# $2 = branch
# $3 = prefix
gmash_subtree_patch(){
  if [ $# == 0 ]; then
    _remote=${GMASH_SUBTREE_PATCH_REMOTE:-""}
    _branch=${GMASH_SUBTREE_PATCH_BRANCH:-"main"}
    _prefix=${GMASH_SUBTREE_PATCH_PREFIX:-""}
    _all=${GMASH_SUBTREE_PATCH_ALL:-"0"}
  else
    _remote=${1:-""}
    _branch=${2:-"main"}
    _prefix=${3:-""}
    _all=${4:-"0"}
  fi

  if [ "$_all" -eq 1 ]; then
    gmash_subtree_pull_all
  else
    if [ -z "$_prefix" ]; then
      echo_err "Missing required '--prefix' parameter"
      return 1
    fi

    if [ -z "$_remote" ]; then
      echo_err "Missing required '--remote' parameter"
      return 1
    fi

    git subtree pull --prefix="$_prefix" "$_remote" "$_branch"
    git pull
    git push
  fi
}

gmash_subtree_pull_all(){
  local gmash_meta_=".gmash/subtree"
  if [ ! -d "$gmash_meta_" ]; then
    echo_err "Subtree metadata directory '$gmash_meta_' not found."
    return 1
  fi

  for conf_file in "$gmash_meta_"/*.conf; do
    # Glob did not detect any files.
    if [ "$conf_file" == "$gmash_meta_/*.conf" ]; then
      conf_file=""
      echo "No subtree metadata found."
      break
    fi

    # Read config values.
    local remote_
    local branch_
    local prefix_
    remote_=$(confread "$conf_file" "remote")
    branch_=$(confread "$conf_file" "branch")
    prefix_=$(confread "$conf_file" "prefix")

    if [ -z "$remote_" ] || [ -z "$branch_" ] || [ -z "$_path" ]; then
      vecho_warn "Incomplete metadata in '$conf_file'. Skipping."
      continue
    fi

    echo "Pulling subtree '$remote_' at '$_path' from '$_url'."
    if ! gmash_subtree_patch \
        "${remote_:-}" \
        "${branch_:-}" \
        "${prefix_:-}"
    then
      echo_err "Failed to pull subtree '$remote_' at '$_path' from '$_url'."
      continue
    fi
  done
  return 0
}

#@doc##########################################################################
  # @func gmash_subtree_new
  # @brief Add subtree to this repo from an existing external git repo.
#@enddoc#######################################################################
gmash_subtree_new(){
  # Get current working repo data
  local api_user_
  api_user_="$(gh_api_user)"
  if [ -z "$api_user_" ]; then
    echo_err "Failed determine GitHub API user. Are you logged in?"
  fi

  local curr_repo_name_
  curr_repo_name_="$(git_curr_repo)"
  if [ -z "$curr_repo_name_" ]; then
    echo_err "Failed to detect active git repo. You must be inside a git repo."
  fi

  local curr_branch_
  curr_branch_="$(git_curr_branch)"

  # Handle input args
  if [ $# == 0 ]; then
    local _prefix=${GMASH_SUBTREE_NEW_PREFIX:-""}
    local _remote=${GMASH_SUBTREE_NEW_REMOTE:-""}
    local _url=${GMASH_SUBTREE_NEW_URL:-""}
    local _branch=${GMASH_SUBTREE_NEW_BR:-"main"}
    local _squash=${GMASH_SUBTREE_NEW_SQUASH:-"0"}
    local _new=${GMASH_SUBTREE_NEW_NEW:-"0"}
  else
    local _prefix=${1:-""}
    local _remote=${2:-""}
    local _url=${3:-""}
    local _branch=${4:-"main"}
    local _squash=${5:-"0"}
    local _new=${6:-"0"}
  fi

  if [ -z "$_prefix" ]; then
    echo_err "Missing required '--prefix' parameter"
    return 1
  fi

  if [ -z "$_remote" ]; then
    echo_err "Missing required '--remote' parameter"
    return 1
  fi

  if [ -z "$_url" ]; then
    _url="https://github.com/$api_user_/$_remote.git"
    vecho_info "URL not provided, targeting subtree remote '$_url'"
  fi

  # Determine the target remote
  #
  # github repo $api_user_/$_remote.git exists & accessible? Use it as the url.
  if git ls-remote "$_url" &> /dev/null; then
      vecho_action "Found existing GitHub repo '$_url'." 1
  else
    # Does the subtree target remote already point to an existing repo ?
    if git remote get-url "$_remote" >/dev/null 2>&1; then
      _url=$(git remote get-url "$_remote" 2>&1)
      vecho_action "Found existing remote '$_remote' with URL '$_url'." 1
      if ! git ls-remote "$_url" &> /dev/null; then
        echo_err "Existing remote '$_remote' URL is not accessible. URL: $_url"
        return 1
      fi
    else
      if [ "$_new" -eq 1 ]; then
        # Create a new GitHub repo with the same name as the remote alias on the api user's
        # GitHub account. Commit of a README.md file(required to be non-empty to add as subtree).
        if command -v gh >/dev/null 2>&1; then
          vecho_action "Creating new GitHub repo '$api_user_/$_remote' for subtree..."
          if gh repo create "$api_user_/$_remote" --private --add-readme --description \
            "[gmash subtree add] Created subtree repository '$api_user_/$_remote' for '$api_user_/$curr_repo_name_:$curr_branch_'"; then
            vecho_action "Created subtree repository '$api_user_/$_remote'."
          else # Unexpected error ?
            echo_err "Failed to create GitHub repository."
            return 1
          fi
        else # gh not installed...
            echo_err "GitHub CLI (gh) not found."
            return 1
        fi
      else
        echo_err "Could not locate subtree remote. Use '--new' to create a repo at '$_url'."
        return 1
      fi
    fi
  fi

  # Guard current remotes, subtrees and parent paths. Overwrite disabled.
  if git config "remote.$_remote.url" > /dev/null; then
    echo_err "Remote '$_remote' already exists."
    return 1
  fi

  if git remote -v | awk '{print $2}' | grep -q "^$_url$"; then
    echo_err "URL '$_url' is already used by another remote."
    return 1
  fi

  if [ -e "$_prefix" ] && [ -n "$(find "$_prefix" -maxdepth 1 -mindepth 1 -print -quit 2>/dev/null)" ]; then
    echo_err "Target path '$_prefix' exists and contains files."
    return 1
  fi

  if git check-ignore -q "$_prefix"; then
    echo_err "Target path '$_prefix' matches gitignore patterns"
    return 1
  fi

  # Perfom the subtree operation
  vecho_process "Adding subtree '$_remote' from '$_url' into '$_prefix'." 1
  git remote add -f "$_remote" "$_url"
  git subtree add --prefix="$_prefix" "$_url" "$_branch"
  git subtree pull --prefix="$_prefix" "$_remote" "$_branch"

  # Add subtree metadata to `.gmash/subtree/$alias.conf`
  vecho_process "Writing subtree metadata to '.gmash/subtree/$_remote.conf'." 1
  local _conf=".gmash/subtree/$_remote.conf"
  confwrite "$_conf" created "$(date)"
  confwrite "$_conf" url "$_url"
  confwrite "$_conf" remote  "$_remote"
  confwrite "$_conf" branch "$_branch"
  confwrite "$_conf" prefix "$_prefix"
  confwrite "$_conf" squash "$_squash"
  confwrite "$_conf" owned  1

  # Commit & push the changes
  git add "$_conf"
  git commit -m "[[gmash][subtree][add]]
 - url: $_url
 - remote: $_remote
 - prefix: $_prefix
 - metadata: $_conf"
  git push

  return 0
}
