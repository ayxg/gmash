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
# @created: 2025/08/31
# @brief Common utils shared between all gmash parsers & commands.
#
# - Custom echo funcs for GMASH_VERBOSE mode/errors.
#@enddoc###########################################################################################


###################################################################################################
# `vecho` : Vebose echo functions
###################################################################################################
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

_get_indent(){
  local level="${1:-0}"

  if ! [[ "$level" =~ ^[0-9]+$ ]]; then
    level=0
  fi

  local _indent=""
  for ((i=0; i<level; i++)); do
    _indent+="    "
  done
  echo "$_indent"
}

vecho(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    echo -e "$(_get_indent "${2:-0}")$1"
  fi
}

echo_err(){
  echo -e "\e[31;1mError:\e[0m $*" >&2;
}

vecho_err(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho "\e[31;1m$1\e[0m" "${2:-0}"
  fi
}

vecho_info(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho "\e[34m$1\e[0m" "${2:-0}"
  fi
}

vecho_action(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho "->$1" "${2:-0}"
  fi
}

vecho_warn(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho "\e[31;1mWarning: \e[0m$1" "${2:-0}"
  fi
}

vecho_process(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho "\e[1m- $1\e[0m" "${2:-0}"
  fi
}

vecho_func(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho "\e[33;1m$1\e[0m" "${2:-0}"
  fi
}

vecho_done(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho "\e[32m$1\e[0m" "${2:-0}"
  fi
}

vecho_section_start() {
    echo -e "\n${PURPLE}┌────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${PURPLE}│${NC} $1${NC}"
    echo -e "${PURPLE}└────────────────────────────────────────────────────────────┘${NC}"
}

vecho_section_end() {
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}\n"
}

###################################################################################################
# git/gh repeated patterns
###################################################################################################

GH_API_USER=""
gh_api_user(){
  if [ -z "$GH_API_USER" ]; then
    GH_API_USER=$(gh api user --jq '.login' 2>/dev/null)
  fi
  printf "%s" "$GH_API_USER"
}

GH_REPO_OWNER=""
gh_repo_owner() {
  if [ -z "$GH_REPO_OWNER" ]; then
    GH_REPO_OWNER=$(gh repo view --json owner --jq '.owner.login' 2>/dev/null)
  fi
  printf "%s" "$GH_REPO_OWNER"
}

git_curr_repo(){
  basename "$(git rev-parse --show-toplevel)" 2>/dev/null
}

git_curr_branch(){
  git rev-parse --abbrev-ref HEAD  2>/dev/null
}

check_repo_access() {
  local _url="$1"

  local owner_repo
  owner_repo=$(echo "$_url" | sed -E '
    s|^https://github.com/||
    s|^git@github.com:||
    s|\.git$||
  ')

  local owner
  owner=$(echo "$owner_repo" | cut -d/ -f1)
  local repo
  repo=$(echo "$owner_repo" | cut -d/ -f2)
  local my_user
  my_user=$(gh_api_user)

  if [ -z "$owner" ] || [ -z "$repo" ]; then
    echo "0"
    return 1
  fi

  if [ "$owner" = "$my_user" ]; then
    echo "1"
    return 0
  fi

  local can_push
  can_push=$(gh api "repos/$owner/$repo" --jq '.permissions.push' 2>/dev/null)

  if [ "$can_push" = "true" ]; then
    echo "1"
  else
    echo "0"
  fi
}