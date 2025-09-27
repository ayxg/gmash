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
#@enddoc#######################################################################

# @brief Patch subtree from its remote repo.
gmash_subtree_patch(){
  if [ $# == 0 ]; then
    _remote=${GMASH_SUBTREE_PATCH_REMOTE:-"origin"}
    _branch=${GMASH_SUBTREE_PATCH_BRANCH:-"main"}
    _path=${GMASH_SUBTREE_PATCH_PATH:-"projects/$_remote"}
  else
    _remote=${1:-"origin"}
    _branch=${2:-"main"}
    _path=${3:-"projects/$_remote"}
  fi

  vecho "\e[33;1mgmash->subtree-patch\e[0m"
  git subtree pull --prefix="$_path" "$_remote" "$_branch"
  git pull
  git push
  vecho "\e[32m\t  ? Subtree patch accepted.\e[0m"
}

#@doc##########################################################################
  # @func gmash_subtree_new
  # @brief Add subtree to this repo from an existing external git repo.
  #
  # Detailed overview of the git process for example subtree 'foo-box'.
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
gmash_subtree_new(){
  vecho_section_start "gmash subtree new"
  local api_user_
  api_user_="$(gh_api_user)"
  if [ -z "$api_user_" ]; then
    vecho_err "Failed determine GitHub API user. Are you logged in?"
  fi

  local curr_repo_name_
  curr_repo_name_="$(git_curr_repo)"
  if [ -z "$curr_repo_name_" ]; then
    vecho_err "Failed to detect active git repo. You must be inside a git repo."
  fi
  vecho_info "Creating subtree for $_user in $curr_repo_name_"

  if [ $# == 0 ]; then
    _user=${GMASH_SUBTREE_NEW_USER:-api_user_}
    _tgtuser=${GMASH_SUBTREE_NEW_TGTUSER:-$_user}
    _path=${GMASH_SUBTREE_NEW_PATH:-""}
    _remote=${GMASH_SUBTREE_NEW_REMOTE:-"origin"}
    _name=${GMASH_SUBTREE_NEW_NAME:-'subtreeDirName'}
    _url=${GMASH_SUBTREE_NEW_URL:-"$_tgtuser/$_name.git"}
    _br=${GMASH_SUBTREE_NEW_BR:-'main'}
    _tgtbr=${GMASH_SUBTREE_NEW_TGTBR:-'main'}
  else
    _url=${1:-"$_remote/$_name.git"}
    _remote=${2:-"origin"}
    _user=${3:-{currentGithubUser}}
    _tgtuser=${4:-$_user}
    _br=${5:-'main'}
    _tgtbr=${6:-'main'}
    _name=${7:-'subtreeDirName'}
  fi
  local curr_repo_name_
  curr_repo_name_=$(basename "$(git rev-parse --show-toplevel)")


  vecho_process "Verifying parameters."
    # If _name is empty, name is the same as remote alias.
    if [ -z "$_name" ]; then
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

    # Is user currently on correct git branch ?
    local _correct_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$_correct_branch" != "$_br" ]; then
      echo_err "Must be on $_br branch (currently on $_correct_branch)."
      return 1
    fi
  vecho_done "Params verified, working on mono branch '$curr_repo_name_/$_tgtbr'." 1

  vecho_info "Final input parameters:" 1
  vecho_info  "- remote:    '$_remote'" 2
  vecho_info  "- path:      '$_path'" 2
  vecho_info  "- url:       '$_url'" 2
  vecho_info  "- user:      '$_user'" 2
  vecho_info  "- tgtuser:   '$_tgtuser'" 2
  vecho_info  "- br:        '$_br'" 2
  vecho_info  "- tgtbr:     '$_tgtbr'" 2
  vecho_info  "- name:      '$_name'." 2

  vecho_process "Getting or creating target subtree repo."
    if [ ! -z "$_url" ]; then # No url, get an existing remote's url or create a new repo at the given remote.
      echo "DEBUG!!!"
      # github repo $_tgtuser/$_name.git exists & accessible? Use it as the url.
      if git ls-remote "https://github.com/$_tgtuser/$_name.git" &> /dev/null; then
          _url="https://github.com/$_tgtuser/$_name.git"
          vecho_action "Found existing GitHub repo '$_tgtuser/$_name.git'. Using it as the subtree remote URL." 1
      else
        # Does the subtree target remote repo already exist ?
        if git remote get-url "$_remote" >/dev/null 2>&1; then
          _url=$(git remote get-url "$_remote" 2>&1)
          vecho_action "Found existing remote '$_remote' with URL '$_url'. Using it as the subtree remote URL." 1
          if ! git ls-remote "$_url" &> /dev/null; then
            echo_err "Existing remote '$_remote' URL is not accessible. URL: $_url"
            return 1
          fi
        else
          # Create a new GitHub repo at '$_tgtuser/$_name.git' with a single
          # commit of a README.md file(required to add as subtree).
          if command -v gh >/dev/null 2>&1; then
            vecho_action "Creating new GitHub repo '$_tgtuser/$_name' for subtree..."
            vecho_func "gh repo create '$_tgtuser/$_name' --private --add-readme --description ..."
            if gh repo create "$_tgtuser/$_name" --private --add-readme --description \
              "[gmash][new-subtree] Generated subtree repository '$_tgtuser/$_name' for '$_user/$curr_repo_name_:$_path'"; then
              _url="https://github.com/$_tgtuser/$_name.git"
            else # Unexpected error ?
              echo_err "Failed to create GitHub repository."
              return 1
            fi
          else # gh not installed...
              echo_err "GitHub CLI (gh) not found. Please create repository manually."
              return 1
          fi
        fi
      fi
    fi
  vecho_done "Target subtree repo URL: '$_url' ready for subtree remote '$_remote'." 1

  vecho_process "Guarding current remotes, subtrees and mono paths. Overwrite disabled."
    if git config "remote.$_remote.url" > /dev/null; then
        vecho_warn "Remote '$_remote' already exists." 1
        echo_err "Remote '$_remote' already exists."
        return 1
    fi
    vecho_action "Remote '$_remote' is unique." 1

    if git remote -v | awk '{print $2}' | grep -q "^$_url$"; then
        vecho_warn "URL '$_url' is already used by another remote." 1
        echo_err "URL '$_url' is already used by another remote."
        return 1
    fi
    vecho_action "URL '$_url' is not used by any existing remote." 1

    if [ -e "$_path" ] && [ -n "$(find "$_path" -maxdepth 1 -mindepth 1 -print -quit 2>/dev/null)" ]; then
        vecho_warn "Target path '$_path' exists and contains files." 1
        echo_err "Target path '$_path' exists and contains files."
        return 1
    fi
    vecho_action "Target path '$_path' is clear." 1

    if git check-ignore -q "$_path"; then
        vecho_warn "Target path '$_path' matches gitignore patterns." 1
        echo_err "Target path '$_path' matches gitignore patterns"
        return 1
    fi
    vecho_action "Target path '$_path' is not ignored by gitignore." 1
  vecho_done "Safe to add subtree." 1

  vecho_process "Adding subtree '$_remote' from '$_url' into '$_path'."
  # Do all the dirty subtree creation git commands... Im still unsure which parts here are necessary.
    vecho_func "git remote add -f '$_remote' '$_url'" 1
    git remote add -f "$_remote" "$_url"

    vecho_func "git subtree add --prefix='$_path' '$_remote' '$_tgtbr'" 1
    git subtree add --prefix="$_path" "$_url" "$_tgtbr"

    vecho_func "git subtree pull --prefix='$_path' '$_remote' '$_tgtbr'" 1
    git subtree pull --prefix="$_path" "$_remote" "$_tgtbr"

    # Add subtree metadata to `.gmash/subtree/$alias.conf`
    vecho_process "Writing subtree metadata to '.gmash/subtree/$_remote.conf'." 1
    local _conf=".gmash/subtree/$_remote.conf"
    confwrite "$_conf" created "$(date)"
    confwrite "$_conf" url "$_url"
    confwrite "$_conf" remote  "$_remote"
    confwrite "$_conf" branch "$_tgtbr"
    confwrite "$_conf" path "$_path"
    confwrite "$_conf" squash false
    confwrite "$_conf" owned  true

    git add "$_conf"
    git commit -m "[gmash][new-subtree] Added subtree \`$_remote\` at \`$_path\` from \`$_url\`. Metadata: \`$_conf\`"

    vecho_func "git push" 1
    git push


  vecho_done "Subtree '$_remote' added to '$_path' and pushed to remote."
  vecho_info "Result metadata:" 1
  vecho_info "[Remote URL]: '$_url'" 2
  vecho_info "[Target Remote Alias]: '$_remote'" 2
  vecho_info "[Target Subtree Branch]: '$_tgtbr'" 2
  vecho_info "[Mono Repo]: '$_user/$curr_repo_name_'" 2
  vecho_info "[Subtree Repo]: '$_tgtuser/$_name'" 2
  vecho_info "[Mono->Subtree Link Path]: '$_path'." 2

  return 0
}
