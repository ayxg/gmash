#!/bin/bash
#@doc---------------------------------------------------------------------------------------------#
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
#-------------------------------------------------------------------------------------------------#
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
#-------------------------------------------------------------------------------------------------#
# @file gmash_dispatch_parsers func
# @created: 2025/08/31
# @brief Dispatches to a specific command sub-parser, by shifting based on last parsed command.
#        Then, calls the target sub-command function.
#@enddoc------------------------------------------------------------------------------------------#

#readonly GMASH_DISPATCH_PARSERS_INVALID_CMD="[gmash][error]: Invalid command specified. Use --help to see commands list."
#readonly GMASH_DISPATCH_PARSERS_INVALID_SUBCMD="[gmash][error]: Invalid sub-command specified. Use --help to see commands list."

gmash_dispatch_parsers(){
  gmash_dev_debug_echo "[gmash_dispatch_parsers: input args]: $*"

  local _argc=$#
  local _cmd=""
  if [ $_argc -gt 0 ]; then
    _cmd=$1
    shift
	  case $_cmd in
      dirs) parse_cmd_dirs "$@"; _cmd=$1; shift; case $_cmd in
        prefix) cmd_parser_dirs_prefix "$@"; cmd_call_dirs_prefix; ;;
        same) cmd_parser_dirs_same "$@"; cmd_call_dirs_same; ;;
        separate) cmd_parser_dirs_separate "$@"; cmd_call_dirs_separate; ;;
        squash) cmd_parser_dirs_squash "$@"; cmd_call_dirs_squash; ;;
        *) echo "$GMASH_DISPATCH_PARSERS_INVALID_SUBCMD"; return 1 ;;
      esac ;;
		  find) parse_cmd_find "$@"; _cmd=$1; shift; case $_cmd in
        duplicate-code) parse_cmd_find_duplicate_code "$@"; cmd_find_duplicate_code; ;;
        gits) parse_cmd_find_gits "$@"; cmd_find_gits; ;;
        sources) parse_cmd_find_sources "$@"; cmd_find_sources; ;;
        *) echo "$GMASH_DISPATCH_PARSERS_INVALID_SUBCMD"; return 1 ;;
      esac ;;
		  gist)

        gmash_parser_gist "$@"
        eval "set -- $GMASH_ARGR"
        # _cmd=$1; shift;
        gmash_dev_debug_echo "[GMASH_ARGR]: $*"
        #eval "set -- $GMASH_ARGR"
        #gmash_dev_debug_echo "[GMASH_ARGR]: $*"

        case $_cmd in
        prepare)
          cmd_parser_gist_prepare "$@"; cmd_call_gist_prepare; ;;
        create)
          cmd_parser_gist_create "$@"; cmd_call_gist_create; ;;
        clone)
          cmd_parser_gist_clone "$@"
          #cmd_call_gist_clone
          ;;
        recover)
          parse_cmd_gist_recover "$@"; cmd_gist_recover; ;;
        upload)
          cmd_parser_gist_upload "$@"; cmd_call_gist_upload; ;;
        *)
          echo "$GMASH_DISPATCH_PARSERS_INVALID_SUBCMD"; return 1 ;;
      esac ;;
      lineage) parse_cmd_lineage "$@"; _cmd=$1; shift; case $_cmd in
        merge) parse_cmd_lineage_merge "$@"; cmd_lineage_merge; ;;
        *) echo "$GMASH_DISPATCH_PARSERS_INVALID_SUBCMD"; return 1 ;;
      esac ;;
      mono) parse_cmd_mono "$@"; _cmd=$1; shift; case $_cmd in
        patch) parse_cmd_mono_patch "$@"; cmd_mono_patch; ;;
        new) parse_cmd_mono_new "$@"; cmd_mono_new; ;;
        *) echo "$GMASH_DISPATCH_PARSERS_INVALID_SUBCMD"; return 1 ;;
      esac ;;
      subtree) parse_cmd_subtree "$@"; _cmd=$1; shift; case $_cmd in
        new) parse_cmd_subtree_new "$@"; cmd_subtree_new; ;;
        patch) parse_cmd_subtree_patch "$@"; cmd_subtree_patch; ;;
        *) echo "$GMASH_DISPATCH_PARSERS_INVALID_SUBCMD"; return 1 ;;
      esac ;;
      *) echo "$GMASH_DISPATCH_PARSERS_INVALID_CMD"; return 1 ;;
	  esac
  fi

  return 0
}