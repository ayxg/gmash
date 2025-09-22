#!/bin/bash
#@doc##########################################################################
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
###############################################################################
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
###############################################################################
# @file gmash->gist parser definition
# @created: 2025/09/02
#@enddoc#######################################################################
source "$GMASH_SOURCE/parser-extensions.sh"

# gmash_def_parser_gist --> gmash_parser_gist
gmash_def_parser_gist(){
    extend_parser
    standard_parser_setup GMASH_GIST_ARGR gmash_gist_help \
      "Usage: gmash [[global-args]...] gist <sub-command> [[args]...]"
  msg -- "  "
  msg -- "Manage GitHub Gists with git-like functionality.
      Use 'upload' to create gists from local files and clone them back as git \
  repos.
      Use 'recover' to create mono-subtree repo from a set of selected gists.
      Use 'gmash mono' and 'gmash subtree' command groups for management of the\
  gist mono-repo.
      Use 'prepare','create' and 'clone' for lower level control. See sub-command\
  help for details."
    msg -- "  "
    msg -- "Globals:"
      param GMASH_GIST_USER -u --user var:"<githubUser>" -- "Global gist source(\
  owner) github user."

    msg -- "  "
    msg -- "Sub-commands:"
      cmd prepare \
          -- "Sets up a new gist with a title.md page with the same name as the \
  target source file(s)."

      cmd create \
        -- "Push all files in a directory as gists to GitHub. Adds a title.md \
  and readme.md by default."

      cmd clone \
          -- "Clones a gist to the local filesystem."

      cmd recover \
          -- "Recover a user's gist(s) from GitHub remotes as git repos."

      cmd upload \
        -- "Upload files to existing gists."

    msg -- "  "
    msg -- "Display:"
      standard_parser_help gmash_gist_help
      disp "GMASH_GIST_VERSION" -v --version \
        -- "[$GMASH_GIST_VERSION] Display command group version."
}

# gmash_def_parser_gist_clone --> gmash_parser_gist_clone
#   |--> gmash_gist_clone
gmash_def_parser_gist_clone(){
    extend_parser
    standard_parser_setup GMASH_GIST_CLONE_ARGR gmash_gist_clone_help \
      "Usage: gmash gist clone [[args]...]"
    msg -- "  "
    msg -- "Clones a gist to the local filesystem as a git repository."
    msg -- "  "
    msg -- "Params:"
      param GMASH_GIST_CLONE_USER -u --user var:"<githubUser>" \
          -- "Target Gist GitHub username (owner)."

      param GMASH_GIST_CLONE_HASH -s --hash var:"<gistHash>" \
          -- "Hash of the gist to clone. Otherwise clones all gists for the \
  user."

      param GMASH_GIST_CLONE_PATH -p --path var:"<clonePath>" \
          -- "Path to clone the gist to. Defaults to current if not passed."

      param GMASH_GIST_CLONE_PREFIX -P --prefix var:"<prefix>" \
        -- "Add a prefix to the cloned gist directory name."

      param GMASH_GIST_CLONE_NAME -n --name var:"<folderName>" \
        -- "Name for the cloned gist directory. Defaults to '[prefix]-[hash]'."
    msg -- "  "
    msg -- "Display:"
      standard_parser_help gmash_gist_clone_help
      disp "GMASH_GIST_CLONE_VERSION" -v --version \
        -- "[$GMASH_GIST_CLONE_VERSION] Display subcommand version."
}

# gmash_def_parser_gist_create --> gmash_parser_gist_create
#   |--> gmash_gist_create
gmash_def_parser_gist_create(){
    extend_parser
    standard_parser_setup GMASH_GIST_CREATE_ARGR gmash_gist_create_help \
      "gmash gist create [<-f <file>>...] [-t [titleFile] | -n [name]] \
  [-r [readmeFile]] [-d [description]] [--no-readme] [--no-title] \
  [-p(--public)]"
    msg -- "  "
    msg -- "Sets up an empty gist with a 'title.md' and 'readme.md' file."
    msg -- "  "
    msg -- "Params:"
      array GMASH_GIST_CREATE_FILE -f --file init:'GMASH_GIST_CREATE_FILE=()'\
  var:"<filePath>" -- "File(s) to upload to the gist."

      param GMASH_GIST_CREATE_TITLE -t --title var:"<titleFile>" \
        -- "File to upload as the 'title.md'. Generates a default if not set."

      param GMASH_GIST_CREATE_NAME -n --name var:"<gistName>" \
        -- "Title for the gist. Will set the name of the title file to \
  '[title].md'. Otherwise, --title file name."

      param GMASH_GIST_CREATE_README -r --readme var:"<readmeFile>" \
        -- "File to upload as the 'README.md'. Generates a default if not set."

      param GMASH_GIST_CREATE_DESC -d --desc var:"<gistDescription>" \
        -- "Description for the new gist."

    msg -- "  "
    msg -- "Flags:"
      gmash_flag GMASH_GIST_CREATE_NOREADME " " --no-readme \
        "Don't generate or add a 'readme.md' file."

      gmash_flag GMASH_GIST_CREATE_NOTITLE " " --no-title \
        "Don't add a 'title.md' file. Implicitly disables 'readme.md' file.\
 Creates an empty gist."

      gmash_flag GMASH_GIST_CREATE_PUBLIC -p --public \
        "Create a public gist. Default is secret."

    msg -- "  "
    msg -- "Display:"
      standard_parser_help gmash_gist_create_help
      disp "GMASH_GIST_CREATE_VERSION" -v --version \
        -- "[$GMASH_GIST_CREATE_VERSION] Display subcommand version."
}

# gmash_def_parser_gist_prepare --> gmash_parser_gist_prepare
#   |--> gmash_gist_prepare
gmash_def_parser_gist_prepare(){
  extend_parser
  standard_parser_setup GMASH_GIST_PREPARE_ARGR gmash_gist_prepare_help \
  "gmash gist prepare [-t [titleFile] | -n [name]] [-r [readmeFile]]\
 [-d [description]] [--no-readme] [--no-title] [-p(--public)]"
  msg -- "  "
  msg -- "  "
  msg -- "Sets up an empty gist with a 'title.md' and 'readme.md' file."
  msg -- "  "
  msg -- "Params:"
  param GMASH_GIST_PREPARE_TITLE -t --title var:"<titleFile>" \
    -- "File to upload as the 'title.md'. Generates a default if not set."
  param GMASH_GIST_PREPARE_NAME -n --name var:"<gistName>" \
    -- "Title for the gist. Will set the name of the title file to\
 '[title].md'. Otherwise, --title file name."
  param GMASH_GIST_PREPARE_README -r --readme var:"<readmeFile>" \
    -- "File to upload as the 'README.md'. Generates a default if not set."
  param GMASH_GIST_PREPARE_DESC -d --desc var:"<gistDescription>" \
    -- "Description for the new gist."
  msg -- "  "
  msg -- "Flags:"
  gmash_flag GMASH_GIST_PREPARE_NOREADME -N --no-readme \
    "Dont generate or add a 'readme.md' file."
  gmash_flag GMASH_GIST_PREPARE_NOTITLE -T --no-title \
    "Dont add a 'title.md' file. Implicitly disables 'readme.md' file.\
 Creates an empty gist."
  gmash_flag GMASH_GIST_PREPARE_PUBLIC -P --public \
    "Create a public gist. Default is secret."
  msg -- "  "
  msg -- "Display:"
    standard_parser_help gmash_gist_prepare_help
    disp "GMASH_GIST_PREPARE_VERSION" -v --version \
      -- "[$GMASH_GIST_PREPARE_VERSION] Display subcommand version."
}


# gmash_def_parser_gist_recover --> gmash_parser_gist_recover
#   |--> gmash_gist_recover
gmash_def_parser_gist_recover(){
      extend_parser
      standard_parser_setup GMASH_GIST_RECOVER_ARGR gmash_gist_recover_help \
        "Usage: gmash gist recover [[args]...]"
      msg -- "  "
      msg -- "Recover a user's gist(s) from GitHub remotes as git repos."
      msg -- "  "
      msg -- "Params:"
        param GMASH_GIST_RECOVER_USER -u --user var:"<githubUser>" \
          -- "Target Gist GitHub username (owner)."

        param GMASH_GIST_RECOVER_HASH -s --hash var:"<gistHash>" \
          -- "Hash of the gist to recover. Otherwise recovers all gists for the \
    user."

        param GMASH_GIST_RECOVER_PATH -p --path var:"<recoverPath>" \
          -- "Path to recover the gist to. Defaults to current if not passed."
      msg -- "  "
      msg -- "Flags:"
        flag GMASH_GIST_RECOVER_SECRET -s --secret on:1 \
          -- "Recover secret gists, only applies when --hash is not specified."

        flag GMASH_GIST_RECOVER_PUBLIC -P --public on:1 \
          -- "Recover public gists, only applies when --hash is not specified."
      msg -- "  "
      msg -- "Display:"
        standard_parser_help gmash_gist_recover_help
        disp "GMASH_GIST_RECOVER_VERSION" -v --version \
          -- "[$GMASH_GIST_RECOVER_VERSION] Display subcommand version."
}


# gmash_def_parser_gist_upload --> gmash_parser_gist_upload
#   |--> gmash_gist_upload
gmash_def_parser_gist_upload(){
    extend_parser
    standard_parser_setup GMASH_GIST_UPLOAD_ARGR gmash_gist_upload_help \
      "Usage: gmash gist upload  <<-f <fileOrPath>> [-f <fileOrPath>]...>
                          [-t <titleFile> | -n <name>]
                          [-r <readmeFile>]
                          [-d <description>]
                          [-p <cloneToPath>]
                          [-u <githubUser>]
                          [--no-readme] [--no-title] [-P(--public)]
                          [-A(--all)] [-a(--asone)][-e(--no-extension)]
                          [-l <limit>]
                          "
    msg -- "  "
    msg -- "Create gists from given file paths and clone them as a local git
  repository. If '--all' is passed, push all files inside dir paths as
  separate gists to GitHub. Use '--no-extension' to combine files with the
  same base name into one gist. Pass '--as-one' to push each dir's files as
  a single gist. Adds a 'title.md' and 'readme.md' by default."
    msg -- "  "
    msg -- "Required:"
      # $1
      array GMASH_GIST_UPLOAD_FILE -f --file init:'GMASH_GIST_UPLOAD_FILE=()'\
  var:"<filePath>" -- "File(s) to upload to the gist."
    msg -- "Optional Params:"
      # $2
      param GMASH_GIST_UPLOAD_TITLE -t --title var:"<titleFile>"\
        -- "File to upload as the 'title.md'. Generates a default if not set."
      # $3
      param GMASH_GIST_UPLOAD_NAME -n --name var:"<gistName>"\
        -- "Title for the gist. Will set the name of the title file to \
  '[title].md'. Otherwise, --title file name."
      # $4
      param GMASH_GIST_UPLOAD_README -r --readme var:"<readmeFile>"\
        -- "File to upload as the 'README.md'. Generates a default if not set."
      # $5
      param GMASH_GIST_UPLOAD_DESC -d --desc var:"<gistDescription>"\
        -- "Description for the new gist."
      # $6
      param GMASH_GIST_UPLOAD_PATH -p --path var:"<cloneToPath>"\
        -- "Path to clone the gist repository to."
      # $7
      param GMASH_GIST_UPLOAD_USER -u --user var:"<githubUser>"\
          -- "Target Gist GitHub username (owner)."
    msg -- "Optional Flags:"
      # $8
      gmash_flag GMASH_GIST_UPLOAD_NOREADME -N --no-readme \
        "Dont generate or add a 'readme.md' file."
      # $9
      gmash_flag GMASH_GIST_UPLOAD_NOTITLE -T --no-title  \
        "Dont add a 'title.md' file. Implicitly disables 'readme.md' file. \
  Creates an empty gist."
      # $10
      gmash_flag GMASH_GIST_UPLOAD_PUBLIC -P --public  \
        "Create a public gist. Default is secret."
    msg -- "'--all' Mode Flags:"
      # $11
      gmash_flag GMASH_GIST_UPLOAD_ALL -A --all  \
        "Interpret all '-f(--file)' paths as directories and push all files \
  inside them as separate gists."
      # $12
      gmash_flag GMASH_GIST_UPLOAD_ASONE -a --asone \
        "Push each dir's files as a single gist."
      # $13
      param GMASH_GIST_UPLOAD_LIMIT -l --limit \
      -- "Maximum number of gists to create. Defaults to 100 (in-case of \
  unintentional overload)."
      # $14
      gmash_flag GMASH_GIST_UPLOAD_NOEXTENSION -e --no-extension \
        "Ignore source file extensions when naming gists and grouping gist \
  sources."
    msg -- "  "
    msg -- "Display:"
      standard_parser_help gmash_gist_recover_help
      disp "GMASH_GIST_RECOVER_VERSION" -v --version \
        -- "[$GMASH_GIST_RECOVER_VERSION] Display subcommand version."
      msg -- " "
      msg -- "Examples:"
      msg -- "Case 1 : Create a gist from one or more files."
      msg -- "            $ gmash gist upload -f file1 -f file2 -n 'foo-gist' \
  -d 'description of my gist'"
      msg -- " "
      msg -- "Case 2 : Create a separate gist for every file in a path, merge \
  files with the same base name."
      msg -- "            $ gmash gist upload -A --no-readme --no-extension"
      msg -- "    Given 'dir1' and 'dir2' contain files 'foo.cpp', 'bar.cpp', \
  and 'foo.hpp', 'bar.hpp' respectively,
      2 gists will be created and cloned to dirs: 'foo' and 'bar' relative to \
  '--path'."
      msg -- " "
      msg -- "Case 3 : Create a separate gist for every directory in a path, \
  merging all files in each dir."
      msg -- "            $ gmash gist upload -A -a -f path1 -f path2"
      msg -- "    Given 'path1' and 'path2' contain dirs 'foo.', 'bar'. 2 \
  gists will be created and cloned to dirs:
        'foo' and 'bar' relative to '--path'."
}
