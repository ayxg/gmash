#!/bin/bash
#@doc##########################################################################
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
###############################################################################
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
###############################################################################
# @file gmash->gist command group
# @created: 2025/08/31
#@enddoc#######################################################################

gmash_gist_clone(){
  if [ $# == 0 ]; then
    local _user=${GMASH_GIST_CLONE_USER:-"$(gh api user --jq '.login')"}
    local _hash=${GMASH_GIST_CLONE_HASH:-""}
    local _path=${GMASH_GIST_CLONE_PATH:-"$(pwd)"}
    local _prefix=${GMASH_GIST_CLONE_PREFIX:-""}
    local _name=${GMASH_GIST_CLONE_NAME:-"unnamed-gist"}
  else
    local _user=${1:-"$(gh api user --jq '.login')"}
    local _hash=${2:-""}
    local _path=${3:-"$(pwd)"}
    local _prefix=${4:-""}
    local _name=${5:-"unnamed-gist"}
  fi
  vecho_func "[$ gmash gist clone]"

  if [ -z "$_user" ]; then
    echo_err "[$ gmash gist clone] Unable to determine authenticated user."
    return 1
  fi

  local dirname_=""
  if [ -n "$_prefix" ]; then
    dirname_="$_prefix-"
  fi

  if [ "$_name" != "unnamed-gist" ] && [ -n "$_name" ]; then
    dirname_="$dirname_$_name"
  else
    dirname_="$dirname_$_hash"
  fi

  vecho_process "Cloning gist to: $_path/$dirname_"
  mkdir -p "$_path"
  cd "$_path" || return 1
  vecho_func "Executing: git clone \"https://gist.github.com/$_user/$_hash.git\" \"$dirname_\""
  git clone "https://gist.github.com/$_user/$_hash.git" "$dirname_"
  cd - || return 1
  return 0
}

# @out 'GMASH_GIST_CREATE_NEW_URL' url of the created gist.
export GMASH_GIST_CREATE_NEW_URL
gmash_gist_create(){
  GMASH_GIST_CREATE_NEW_URL=""
  if [ $# == 0 ]; then
    local _title=${GMASH_GIST_CREATE_TITLE:-""}
    local _name=${GMASH_GIST_CREATE_NAME:-"unnamed-gist"}
    local _readme=${GMASH_GIST_CREATE_README:-""}
    local _noreadme=${GMASH_GIST_CREATE_NOREADME:-"0"}
    local _notitle=${GMASH_GIST_CREATE_NOTITLE:-"0"}
    local _public=${GMASH_GIST_CREATE_PUBLIC:-"0"}
    local _desc=${GMASH_GIST_CREATE_DESC:-""}
    local _files=()
    _files=("${GMASH_GIST_CREATE_FILE[@]}")
  else
    local _title=${1:-""}
    local _name=${2:-"unnamed-gist"}
    local _readme=${3:-""}
    local _noreadme=${4:-"0"}
    local _notitle=${5:-"0"}
    local _public=${6:-"0"}
    local _desc=${7:-""}
    local _files=()
    _files=("${GMASH_GIST_CREATE_FILE[@]}")
  fi

  vecho_func "[$ gmash gist create]"
  # Validate that none of the source files are empty or else gist will fail.
  for file in "${_files[@]}"; do
    if [ ! -f "$file" ]; then
      echo_err "[$ gmash gist create] Source file does not exist: $file"
      return 1
    fi
    if [ ! -s "$file" ]; then
      echo_err "[$ gmash gist create] Source file is empty: $file". You must provide non-empty source files.
      return 1
    fi
  done

  if ! gmash_gist_prepare \
      "${_title:-}" \
      "${_name:-}" \
      "${_readme:-}" \
      "${_noreadme:-}" \
      "${_notitle:-}" \
      "${_public:-}" \
      "${_desc:-}"
  then
    echo_err "[$ gmash gist create] Failed to prepare gist."
    return 1
  fi

  local new_url_
  new_url_=$(echo "$GMASH_GIST_PREPARE_NEW_URL" | tail -n 1)
  vecho_process "Adding source files to gist: $new_url_"
  for file in "${_files[@]}"; do
    vecho_action "Adding : $file"
    vecho_func "Executing: gh gist edit \"$new_url_\" -a \"$file\""
    gh gist edit "$new_url_" -a "$file"
  done

  vecho_done "Gist created:"
  echo "$new_url_"
  GMASH_GIST_CREATE_NEW_URL="$new_url_"
  return 0
}

# @echo-out url of the prepared gist.
export GMASH_GIST_PREPARE_NEW_URL
gmash_gist_prepare(){
  GMASH_GIST_PREPARE_NEW_URL=""
  if [ $# == 0 ]; then
    local _title=${GMASH_GIST_PREPARE_TITLE:-""}
    local _name=${GMASH_GIST_PREPARE_NAME:-"unnamed-gist"}
    local _readme=${GMASH_GIST_PREPARE_README:-""}
    local _noreadme=${GMASH_GIST_PREPARE_NOREADME:-"0"}
    local _notitle=${GMASH_GIST_PREPARE_NOTITLE:-"0"}
    local _public=${GMASH_GIST_PREPARE_PUBLIC:-"0"}
    local _desc=${GMASH_GIST_PREPARE_DESC:-""}
  else
    local _title=${1:-""}
    local _name=${2:-"unnamed-gist"}
    local _readme=${3:-""}
    local _noreadme=${4:-"0"}
    local _notitle=${5:-"0"}
    local _public=${6:-"0"}
    local _desc=${7:-""}
  fi

  local has_desc_=""
  local local_tempdir_=""

  local_tempdir_="$(mktemp -d -t gist-prepare-XXXX)"
  _cleanup() {
    if [ -n "$local_tempdir_" ] && [ -d "$local_tempdir_" ]; then
      rm -rf "$local_tempdir_"
    fi
  }

  vecho_func "[$ gmash gist prepare]"
  vecho_info "Input Arguments:
        Title: $_title
        Name: $_name
        README: $_readme
        No README: $_noreadme
        No Title: $_notitle
        Public: $_public
        Description: $_desc
        Temp Dir: $local_tempdir_"

  if [ -n "$_desc" ]; then
    has_desc_="-d"
    vecho_action "Enabling description."
  fi

  if [ -n "$_public" ] && [ "$_public" != "false" ] && [ "$_public" != "0" ]; then
    _public="--public"
    vecho_action "Creating public gist."
  else
    _public=""
    vecho_action "Creating secret gist."
  fi

  local _title_file=""
  if [ "$_notitle" -eq 0 ]; then
    vecho_action "Adding title file."
    if [ -z "$_title" ]; then
      if [ -z "$_name" ]; then
        _title_file="$local_tempdir_/\!_TITLE.md"
        echo "# $_name" > "$_title_file"
        vecho_action "No name provided, using default title file name: \!_TITLE.md"
      else
        _title_file="$local_tempdir_/\!$_name.md"
        echo "# $_name" > "$_title_file"
        vecho_action "No title file provided, using name as title file name: \!$_name.md"
      fi
    else
      vecho_action "Title file provided."
      if [ -z "$_name" ]; then
        vecho_action "Appending ! to input title file."
        _title_file="$local_tempdir_/\!$(basename "$_title").md"
        cp "$_title" "$_title_file"
      else
        cp "$_title" "$local_tempdir_/\!$_name.md"
        _title_file="$local_tempdir_/\!$_name.md"
        vecho_action "Copying title file to temp with name: \!$_name.md"
      fi
    fi

    if [ "$_noreadme" -eq 0 ]; then # Enable readme.
      vecho_action "Adding README file."
      if [ -z "$_readme" ]; then # No readme file provided.
        _readme="$local_tempdir_/README.md"
        echo "# $_name" > "$_readme"
        vecho_action "No readme file provided, using default $_readme."
      else
        cp "$_readme" "$local_tempdir_/README.md"
        _readme="$local_tempdir_/README.md"
        vecho_action "Copying readme file to temp as $_readme."
      fi
    else
      _readme=""
    fi
  else
    _title_file=""
    _readme=""
  fi

  if [ -n "$_title_file" ] && [ ! -f "$_title_file" ]; then
    echo_err "Title file does not exist: $_title_file"
    _cleanup
    return 1
  fi
  if [ -n "$_readme" ] && [ ! -f "$_readme" ]; then
    echo_err "README file does not exist: $_readme"
    _cleanup
    return 1
  fi

  # Build gh command
  local cmd_args=("gh" "gist" "create")
  if [ -n "$_title_file" ] && [ -f "$_title_file" ]; then
    cmd_args+=("$_title_file")
  fi

  if [ -n "$has_desc_" ] && [ -n "$_desc" ]; then
    cmd_args+=("$has_desc_" "\"$_desc\"")
  fi

  if [ -n "$_public" ]; then
    cmd_args+=("$_public")
  fi

  vecho_info "Processed Arguments:
        Title: $_title
        Name: $_name
        README: $_readme
        No README: $_noreadme
        No Title: $_notitle
        Public: $_public
        Description: $_desc
        Temp Dir: $local_tempdir_"

  # Run command
  vecho_func "Executing: ${cmd_args[*]}"
  local _gh_output=""
  _gh_output=$("${cmd_args[@]}" 2>&1)
  exit_code=$?

  # Extract the gist URL from the output
  local _gist_url=""
  if [ $exit_code -eq 0 ] ; then
      # Extract the URL line
      _gist_url=$(echo "$_gh_output" | grep -E '^https://gist.github.com/' | tail -n1)

      if [ -n "$_gist_url" ]; then
          vecho_done "Gist created successfully: $_gist_url"
      else
          # Fallback: try to find URL in any line
          _gist_url=$(echo "$_gh_output" | grep -o 'https://gist.github.com/[a-zA-Z0-9/]\+' | head -n1)
          if [ -n "$_gist_url" ]; then
              vecho_done "Gist created successfully: $_gist_url"
          else
              vecho_warn "Gist created but URL not found in output"
          fi
      fi

    # add the readme after cause it seems like its random which file is the title otherwise...
    if [ -n "$_readme" ] && [ -f "$_readme" ]; then
      gh gist edit "$_gist_url" -a "$_readme"
    fi
  else
      echo_err "Failed to create gist (exit code: $exit_code)"
      echo_err "Output: $_gh_output"
      return $exit_code
  fi
  _cleanup

  # Output
  echo "$_gist_url"
  GMASH_GIST_PREPARE_NEW_URL="$_gist_url"
}

gmash_gist_recover(){
  if [ $# == 0 ]; then
    _user=${GMASH_GIST_RECOVER_USER:-"$(gh api user --jq '.login')"}
    _hash=${GMASH_GIST_RECOVER_HASH:-""}
    _path=${GMASH_GIST_RECOVER_PATH:-"$(pwd)"}
    _public=${GMASH_GIST_RECOVER_PUBLIC:-0}
    _secret=${GMASH_GIST_RECOVER_SECRET:-0}
    _limit=${GMASH_GIST_RECOVER_LIMIT:-1000}
  else
    _user=${1:-"$(gh api user --jq '.login')"}
    _hash=${2:-""}
    _path=${3:-"$(pwd)"}
    _public=${4:-0}
    _secret=${5:-0}
    _limit=${6:-1000}
  fi

  mkdir -p "$_path"
  cd "$_path" || return 1

  if [ "$_public" = 1 ]; then
    _public="--public"
  else
    _public=""
  fi

  if [ "$_secret" = 1 ]; then
    _public="--secret"
  fi

  gist_list_=$(gh gist list -L "$_limit" "$_public" | awk '
  NR > 1 {
      hash = $1
      desc = ""
      for (i=2; i<=NF; i++) {
          desc = desc $i " "
          if ($(i+1) ~ /^[0-9]+$/ && $(i+2) ~ /^file/) { break }
          if ($i ~ /^[0-9]+$/ && $(i+1) ~ /^file/) { break }
      }
      sub(/[ \t]+$/, "", desc)
      print hash "\t" desc
  }')

  if [ -z "$gist_list_" ]; then
      echo_err "No gists found, or failed to fetch gist list."
      return 1
  fi

  echo "$gist_list_" | while IFS=$'\t' read -r gist_id_ gist_desc_; do
      if [ -z "$gist_desc_" ] || [ "$gist_desc_" = " " ]; then
          dir_name_="unnamed-gist-$gist_id_"
      else
          dir_name_=$(echo "$gist_desc_" | tr -cd 'a-zA-Z0-9 _-' | sed 's/ /_/g')
          dir_name_="${dir_name_}-$gist_id_"
      fi

      mkdir -p "$dir_name_"
      cd "$dir_name_" || return 1
      git clone "https://gist.github.com/$_user/$gist_id_.git"
      cd .. || return 1
  done

  cd - || return 1
}

gmash_gist_upload(){
  if [ $# == 0 ]; then
    local _files=()
    _files=("${GMASH_GIST_UPLOAD_FILE[@]}")

    local _title=${GMASH_GIST_UPLOAD_TITLE:-""}
    local _name=${GMASH_GIST_UPLOAD_NAME:-"unnamed-gist"}
    local _readme=${GMASH_GIST_UPLOAD_README:-""}
    local _desc=${GMASH_GIST_UPLOAD_DESC:-""}
    local _path=${GMASH_GIST_UPLOAD_PATH:-""}
    local _user=${GMASH_GIST_UPLOAD_USER:-"$(gh api user --jq '.login')"}

    local _noreadme=${GMASH_GIST_UPLOAD_NOREADME:-"0"}
    local _notitle=${GMASH_GIST_UPLOAD_NOTITLE:-"0"}
    local _public=${GMASH_GIST_UPLOAD_PUBLIC:-"0"}

    local _all=${GMASH_GIST_UPLOAD_ALL:-"0"}
    local _asone=${GMASH_GIST_UPLOAD_ASONE:-"0"}
    local _limit=${GMASH_GIST_UPLOAD_LIMIT:-"100"}
    local _noextension=${GMASH_GIST_UPLOAD_NOEXTENSION:-"0"}
  else
    local _files=()
    _files=("${GMASH_GIST_UPLOAD_FILE[@]}")

    local _title=${1:-""}
    local _name=${2:-"unnamed-gist"}
    local _readme=${3:-""}
    local _desc=${4:-""}
    local _path=${5:-""}
    local _user=${6:-"$(gh api user --jq '.login')"}

    local _noreadme=${7:-"0"}
    local _notitle=${8:-"0"}
    local _public=${9:-"0"}

    local _all=${10:-"0"}
    local _asone=${11:-"0"}
    local _limit=${12:-"100"}
    local _noextension=${13:-"0"}
  fi

  # single repo mode
  if [ "$_all" == 0 ]; then
    Z_GMASH_GIST_UPLOAD_SINGLE_FILES=("${_files[@]}")
    z_gmash_gist_upload_single \
      "${_title:-}" \
      "${_name:-}" \
      "${_readme:-}" \
      "${_desc:-}" \
      "${_path:-}" \
      "${_user:-}" \
      "${_noreadme:-}" \
      "${_notitle:-}" \
      "${_public:-}"
  # --all mode
  elif [ "$_asone" == 0 ]; then
    # --all : Scan each path for source files and create a gist for each.
    if [ "$_noextension" == 0 ]; then
      if [ "${#_files[@]}" -eq 0 ]; then
        _files=("$(pwd)")
        vecho_warn "No input folders provided, defaulting to current working directory: ${_files[0]}"
      fi

      for folder in "${_files[@]}"; do
        vecho_process "Scanning for source files in $folder"
        for f in "$folder"/*; do
          if [[ -f "$f" && ! -d "$f" ]]; then
            local folder_name
            folder_name=$(basename "$f")
            local file_array=()
            file_array=("$f")
            Z_GMASH_GIST_UPLOAD_SINGLE_FILES=("${file_array[@]}")
            if ! z_gmash_gist_upload_single \
                  "${_title:-}" \
                  "${folder_name:-}" \
                  "${_readme:-}" \
                  "${_desc:-}" \
                  "${_path:-}" \
                  "${_user:-}" \
                  "${_noreadme:-}" \
                  "${_notitle:-}" \
                  "${_public:-}"
            then
              echo "Skipping file due to error: $f"
            fi
            Z_GMASH_GIST_UPLOAD_SINGLE_FILES=()
          fi
        done
      done
    # --all + --no-extension mode : Collect all files with the same name ignoring extension into the same gist
    else
      if [ "${#_files[@]}" -eq 0 ]; then
        _files=("$(pwd)")
        vecho_warn "No input folders provided, defaulting to current working directory: ${_files[0]}"
      fi

      declare -A file_map
      for folder in "${_files[@]}"; do
        for f in "$folder"/*; do
          base_name=$(basename "$f")
          name_no_ext="${base_name%%.*}"
          if [[ ! -v file_map[$name_no_ext] ]]; then
            file_map["$name_no_ext"]="$f"
            vecho_action "Mapping gist source: '$f' -> '$name_no_ext'"
          else
            file_map["$name_no_ext"]+=$'\n'"$f"
            vecho_action "Mapping gist source: '$f' -> '$name_no_ext'"
          fi
        done
      done

      echo "Prepared ${!file_map[*]} gists to create."
      for name_no_ext in "${!file_map[@]}"; do
        vecho_process "Creating gist : $name_no_ext"
        echo "test"
        mapfile -t Z_GMASH_GIST_UPLOAD_SINGLE_FILES <<< "${file_map[$name_no_ext]}"
    vecho_action "Files for '$name_no_ext': ${Z_GMASH_GIST_UPLOAD_SINGLE_FILES[*]}"
        z_gmash_gist_upload_single \
          "${_title:-}" \
          "${name_no_ext:-}" \
          "${_readme:-}" \
          "${_desc:-}" \
          "${_path:-}" \
          "${_user:-}" \
          "${_noreadme:-}" \
          "${_notitle:-}" \
          "${_public:-}"
            local exit_code=$?
            vecho_action "z_gmash_gist_upload_single exited with code: $exit_code"

        Z_GMASH_GIST_UPLOAD_SINGLE_FILES=()
           vecho_action "FINISHED Processing '$name_no_ext'"
      done
    fi
  # --all + --as-one mode
  else
    # Collect all files in each passed folder as a separate gist.
    for folder in "${_files[@]}"; do
      if [ -d "$folder" ]; then
        mapfile -t files_array < <(find "$folder" -maxdepth 1 -type f)
        if [ "${#files_array[@]}" -eq 0 ]; then
          echo "[warning][gist-upload] No files found in directory '$folder'. Skipping."
          continue
        fi
        local _new_url
        _new_url=$(cmd_call_gist_create \
          "${files_array[@]}" \
          "${_title:-}" \
          "$(basename "$folder")" \
          "${_readme:-}" \
          "${_noreadme:-}" \
          "${_notitle:-}" \
          "${_public:-}" \
          "${_desc:-}")
        GIST_CREATED_URL=$(echo "$_new_url" | tail -n 1)
        _hash=$(echo "$GIST_CREATED_URL" | awk -F/ '{print $NF}')
        empty_dummy=""
        GMASH_GIST_UPLOAD_NAME="" # reset --name arg used in gist_create
        cmd_call_gist_clone  \
          "${_user:-}" \
          "${_hash:-}" \
          "${_path:-}" \
          "$(basename "$folder")" # pass the name to $4:prefix
          ${empty_dummy:-}
        echo "$GIST_CREATED_URL" # echo OUTPUT
      fi
    done
  fi
  vecho_done "Success."
  return 0
}

export Z_GMASH_GIST_UPLOAD_SINGLE_FILES
export Z_GMASH_GIST_UPLOAD_NEW_URL
z_gmash_gist_upload_single(){
  if [ $# == 0 ]; then
    local _files=()
    _files=("${Z_GMASH_GIST_UPLOAD_SINGLE_FILES[@]}")

    local _title=${GMASH_GIST_UPLOAD_TITLE:-""}
    local _name=${GMASH_GIST_UPLOAD_NAME:-"unnamed-gist"}
    local _readme=${GMASH_GIST_UPLOAD_README:-""}
    local _desc=${GMASH_GIST_UPLOAD_DESC:-""}
    local _path=${GMASH_GIST_UPLOAD_PATH:-""}
    local _user=${GMASH_GIST_UPLOAD_USER:-"$(gh api user --jq '.login')"}

    local _noreadme=${GMASH_GIST_UPLOAD_NOREADME:-"0"}
    local _notitle=${GMASH_GIST_UPLOAD_NOTITLE:-"0"}
    local _public=${GMASH_GIST_UPLOAD_PUBLIC:-"0"}
  else
    local _files=()
    _files=("${Z_GMASH_GIST_UPLOAD_SINGLE_FILES[@]}")

    local _title=${1:-""}
    local _name=${2:-"unnamed-gist"}
    local _readme=${3:-""}
    local _desc=${4:-""}
    local _path=${5:-""}
    local _user=${6:-"$(gh api user --jq '.login')"}

    local _noreadme=${7:-"0"}
    local _notitle=${8:-"0"}
    local _public=${9:-"0"}
  fi

  local _new_url
  export GMASH_GIST_CREATE_FILE=("${_files[@]}")
  if ! gmash_gist_create \
    "${_title:-}" \
    "${_name:-}" \
    "${_readme:-}" \
    "${_noreadme:-}" \
    "${_notitle:-}" \
    "${_public:-}" \
    "${_desc:-}"; then
    echo_err "[$ gmash gist create] Failed to create gist."
    return 1
  fi

  _new_url="$GMASH_GIST_CREATE_NEW_URL"

  GIST_CREATED_URL=$(echo "$_new_url" | tail -n 1)
  _hash=$(echo "$GIST_CREATED_URL" | awk -F/ '{print $NF}')
  empty_dummy=""
  GMASH_GIST_UPLOAD_NAME="" # reset --name arg used in gist_create
  gmash_gist_clone  \
    "${_user:-}" \
    "${_hash:-}" \
    "${_path:-}" \
    "${_name:-}" # pass the name to $4:prefix
    ${empty_dummy:-}
  echo "$GIST_CREATED_URL" # echo OUTPUT
}