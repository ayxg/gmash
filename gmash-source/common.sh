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

vecho(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    echo -e "$@"
  fi
}

echo_err(){
  echo -e "\e[31;1mError:\e[0m $*" >&2;
}

vecho_err(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho -e "\e[31;1m" "$@" "\e[0m"
  fi
}

vecho_info(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho -e "\e[34m    ⓘ " "$@" "\e[0m"
  fi
}

vecho_action(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho -e "        -> " "$@"
  fi
}

vecho_warn(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho -e "\e[33;1m" "$@" "\e[0m"
  fi
}

vecho_process(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho -e "\e[35m    ⚙ " "$@" "\e[0m"
  fi
}

vecho_func(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho -e "\e[33;1m" "$@" "\e[0m"
  fi
}

vecho_done(){
  if [ "$GMASH_VERBOSE" = 1 ]; then
    vecho -e "\e[32m\t  ✓ " "$@" "\e[0m"
  fi
}