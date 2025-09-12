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
  if [ $# == 0 ]; then
    _url=${GMASH_SUBTREE_NEW_URL:-"$_remote/$_name.git"}
    _remote=${GMASH_SUBTREE_NEW_REMOTE:-"origin"}
    _user=${GMASH_SUBTREE_NEW_USER:-{currentGithubUser}}
    _tgtuser=${GMASH_SUBTREE_NEW_TGTUSER:-$_user}
    _br=${GMASH_SUBTREE_NEW_BR:-'main'}
    _tgtbr=${GMASH_SUBTREE_NEW_TGTBR:-'main'}
    _name=${GMASH_SUBTREE_NEW_NAME:-'subtreeDirName'}
  else
    _url=${1:-"$_remote/$_name.git"}
    _remote=${2:-"origin"}
    _user=${3:-{currentGithubUser}}
    _tgtuser=${4:-$_user}
    _br=${5:-'main'}
    _tgtbr=${6:-'main'}
    _name=${7:-'subtreeDirName'}
  fi
  local _curr_repo_name
  _curr_repo_name=$(basename "$(git rev-parse --show-toplevel)")

  vecho_func "gmash->new->subtree"
  veco_info "Input Arguments:
    --remote='$_remote',
    --path='$_path',
    --url='$_url',
    --user='$_user',
    --tgtuser='$_tgtuser',
    --br='$_br',
    --tgtbr='$_tgtbr',
    --name='$_name'."


  vecho_process "Verifying parameters."
    # If _name is empty, name is the same as remote alias.
    if [ -z "$_name" ]; then
      _name="$_remote"
      vecho_action "Defaulting subtree name($_name) to remote alias($_remote)."
    fi
    if [ -z "$_tgtuser" ]; then
      _tgtuser="$_user"
      vecho_action "Defaulting target user($_tgtuser) to source user($_user)."
    fi
    if [ -z "$_br" ]; then
      _br="main"
      vecho_action "Defaulting mono repo branch($_br) to 'main'."
    fi
    if [ -z "$_tgtbr" ]; then
      _tgtbr="main"
      vecho_action "Defaulting target subtree branch($_tgtbr) to 'main'."
    fi
    if [ -z "$_path" ]; then
      _path="projects/$_name"
      vecho_action "Defaulting subtree path($_path) to 'projects/$_name'."
    fi

    # Is user currently on correct git branch ?
    local _correct_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$_correct_branch" != "$_tgtbr" ]; then
      echo_err "[gmash][new-subtree][error]: Must be on $_tgtbr branch (currently on $_correct_branch)."
      return 1
    fi
  vecho_done "Params verified, working on mono branch '$_curr_repo_name/$_tgtbr'."

  vecho_info "Final input parameters:
    --remote='$_remote',
    --path='$_path',
    --url='$_url',
    --user='$_user',
    --tgtuser='$_tgtuser',
    --br='$_br',
    --tgtbr='$_tgtbr',
    --name='$_name'."

  vecho_process "Getting/Creating target subtree repo."
    if [ -z "$_url" ]; then # No url, get an existing remote's url or create a new repo at the given remote.
      # github repo $_tgtuser/$_name.git exists & accessible? Use it as the url.
      if git ls-remote "https://github.com/$_tgtuser/$_name.git" &> /dev/null; then
          _url="https://github.com/$_tgtuser/$_name.git"
          vecho_action "Found existing GitHub repo '$_tgtuser/$_name.git'. Using it as the subtree remote URL."
      else
        # Does the subtree target remote repo already exist ?
        if git remote get-url "$_remote" >/dev/null 2>&1; then
          _url=$(git remote get-url "$_remote" 2>&1)
          vecho_action "Found existing remote '$_remote' with URL '$_url'. Using it as the subtree remote URL."
          if ! git ls-remote "$_url" &> /dev/null; then
            echo_err "[gmash][new-subtree][error]: Existing remote '$_remote' URL is not accessible. URL: $_url"
            return 1
          fi
        else
          # Create a new GitHub repo at '$_tgtuser/$_name.git' with a single
          # commit of a README.md file(required to add as subtree).
          if command -v gh >/dev/null 2>&1; then
            vecho_action "Creating new GitHub repo '$_tgtuser/$_name' for subtree..."
            vecho_func "gh repo create '$_tgtuser/$_name' --private --add-readme --description ..."
            if gh repo create "$_tgtuser/$_name" --private --add-readme --description \
              "[gmash][new-subtree] Generated subtree repository '$_tgtuser/$_name' for '$_user/$_curr_repo_name:$_path'"; then
              _url="https://github.com/$_tgtuser/$_name.git"
            else # Unexpected error ?
              echo_err "[gmash][new-subtree][error]: Failed to create GitHub repository."
              return 1
            fi
          else # gh not installed...
              echo_err "[gmash][new-subtree][error]: GitHub CLI (gh) not found. Please create repository manually."
              return 1
          fi
        fi
      fi
    fi
  vecho_done "Target subtree repo URL: '$_url' ready for subtree remote '$_remote'."

  vecho "Guarding current remotes, subtrees and mono paths. Overwrite disabled."
    if git config "remote.$_remote.url" > /dev/null; then
        echo_err "[gmash][new-subtree][error]: Remote '$_remote' already exists."
        return 1
    fi
    vecho_action "Remote '$_remote' is unique."

    if git remote -v | awk '{print $2}' | grep -q "^$_url$"; then
        echo_err "[gmash][new-subtree][error]: URL '$_url' is already used by another remote."
        return 1
    fi
    vecho_action "URL '$_url' is not used by any existing remote."

    if [ -e "$_path" ] && [ -n "$(find "$_path" -maxdepth 1 -mindepth 1 -print -quit 2>/dev/null)" ]; then
        echo_err "[gmash][new-subtree][error]: Target path '$_path' exists and contains files."
        return 1
    fi
    vecho_action "Target path '$_path' is clear."

    if git check-ignore -q "$_path"; then
        echo_err "[gmash][new-subtree][error]: Target path '$_path' matches gitignore patterns"
        return 1
    fi
    vecho_action "Target path '$_path' is not ignored by gitignore."
  vecho_done "Safe to add subtree.\e[0m"

  # Do all the dirty subtree creation git commands... Im still unsure which parts here are necessary.
    vecho_func "git remote add -f '$_remote' '$_url'"
    git remote add -f "$_remote" "$_url"

    vecho_func "git subtree add --prefix='$_path' '$_remote' '$_tgtbr'"
    git subtree add --prefix="$_path" "$_url" "$_tgtbr"

    vecho_func "git subtree pull --prefix='$_path' '$_remote' '$_tgtbr'"
    git subtree pull --prefix="$_path" "$_remote" "$_tgtbr"

    vecho_func "git push"
    git push

    vecho_done "Subtree '$_remote' added to '$_path' and pushed to remote.\e[0m"
    vecho_info "Result metadata:\
      [Remote URL]: '$_url'
      [Target Remote Alias]: '$_remote'
      [Target Subtree Branch]: '$_tgtbr'
      [Mono Repo]: '$_user/$_curr_repo_name'
      [Subtree Repo]: '$_tgtuser/$_name'
      [Mono->Subtree Link Path]: '$_path'.\e[0m"

  return 0
}
