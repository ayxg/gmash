## Project Overview

gmash (Git Smash) provides a suite of Bash scripts that streamline common Git and GitHub repository operations. It standardizes workflows, reduces boilerplate, and exposes consistent version metadata across your projects.

### What Is gmash?
gmash bundles environment setup, global variables, version metadata and helper functions into a lightweight CLI for:
- Repository creation and cloning  
- Branching, syncing and pushing  
- Automated version display  
- GitHub interaction (PRs, issues, forks)

### Why It Exists
Developers spend time writing repetitive Git commands and managing multiple remotes. gmash centralizes these tasks into reusable scripts, enforcing consistency and minimizing context‐switching.

### Primary Capabilities
- Environment bootstrap with global variables (configured in `gmash-source/global.sh`)  
- Hierarchical version metadata display  
- High‐level GitHub operations (init, fork, pull‐request)  
- Customizable hooks for project‐specific workflows

### Supported Platforms
- Any Unix‐like OS with Bash 4+ (Linux, macOS, WSL)  
- Requires standard GNU utilities (`git`, `curl`, `sed`, etc.)

### Licensing
gmash is licensed under the GNU Affero General Public License v3.0.  
You may copy, modify, and distribute under AGPLv3 terms; network use triggers source availability requirements.  
See LICENSE.txt for full details.

### Quick Start Example

Clone the repository and verify the installed version:

```shell
# Clone gmash
git clone https://github.com/ayxg/gmash.git
cd gmash

# Add to PATH or invoke directly
chmod +x gmash
./gmash --version
# Output example:
# gmash version 0.4.1
# build: 2025-09-01
```

Ensure `gmash-source` remains alongside the main script to load environment settings and version metadata.
## Getting Started

Follow these steps to install gmash, compile its parsers, verify your setup, and run your first command.

### Prerequisites

- Bash shell  
- gengetopt (or gengetoptions) installed  
- Git client  

Verify gengetopt:  
```bash
gengetopt --version
```

### 1. Clone the Repository

```bash
git clone https://github.com/ayxg/gmash.git
cd gmash
```

### 2. Add gmash to Your PATH

Add the project root to your `PATH` so you can invoke `gmash` from any location.

For a temporary session:
```bash
export PATH="$PWD:$PATH"
```

To make this permanent, append to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
echo 'export PATH="~/path/to/gmash:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Compile Parsers

gmash uses gengetopt to generate CLI parsers for its commands. Run the compile script:

```bash
bash gmash-source/gmash-compile.sh
```

This produces updated parser source files under `gmash-source/parser/` and integrates them into the main dispatcher.

### 4. Verify Installation

Check that `gmash` is on your `PATH` and that parsers load correctly:

```bash
gmash --help
```

Expected output shows global options and a list of subcommands:
```
Usage: gmash [OPTIONS] COMMAND [ARGS]
Global options:
  -h, --help     Show help
  -v, --version  Show version
Commands:
  dirs      Manage repository directory shortcuts
  find      Search across repositories
  gist      Upload/downloader GitHub gists
  lineage   Display repository ancestry
  mono      Apply operations across many repos
  subtree   Operate on Git subtrees
```

### 5. Run Your First Command

List all configured directory shortcuts:
```bash
gmash dirs list
```

Search for the string “TODO” across all repos in your workspace:
```bash
gmash find --query TODO --path ~/projects
```

Both commands should execute without errors. You’re now ready to explore gmash’s full feature set!
## Command Reference

This section describes every gmash sub-command, its flags, arguments, workflows and examples.

### dirs prefix

Purpose  
Add a specified prefix to each top-level file in a directory (or to a single file).

Synopsis  
gmash dirs prefix --prefix &lt;prefix&gt; [--path &lt;fileOrFolder&gt;]

Options  
-p, --prefix   Prefix string to prepend (required)  
-P, --path     Target file or directory. Defaults to current working directory.  

Environment Overrides  
You can also set these via environment variables before invoking the command:  
• GMASH_DIRS_PREFIX_PREFIX – equivalent to --prefix  
• GMASH_DIRS_PREFIX_PATH   – equivalent to --path  

Behavior  
1. Validates that a non-empty prefix is provided.  
2. Verifies the target path exists.  
3. If the path is a file, renames only that file.  
4. If the path is a directory, renames every regular file at its top level.  
5. Emits errors on missing prefix/path or non-existent targets, returning non-zero.

Examples  

Add “new_” to every file in the current directory:  
```bash
gmash dirs prefix -p new_
```

Prefix a single file:  
```bash
gmash dirs prefix --prefix v2_ --path ./release.tar.gz
```

Use environment variables instead of flags:  
```bash
export GMASH_DIRS_PREFIX_PREFIX="backup_"
export GMASH_DIRS_PREFIX_PATH="/var/logs"
gmash dirs prefix
```

Verbose Output  
If GMASH_VERBOSITY is set to “info” or higher, you’ll see steps logged via vecho_* calls:  
• Input arguments  
• Each rename action  
• Final “Success.” message

Failure Cases  
• Missing --prefix: prints “--prefix argument is required.”  
• Non-existent path: prints “Target path ‘…’ does not exist.”  
• Other filesystem errors: reported by mv(1) and wrapped by vecho_warn.

---

### gmash find duplicate-code

Purpose  
Locate duplicated C++ code blocks in a directory tree using Simian, helping enforce DRY principles.

Synopsis  
gmash find duplicate-code [-p &lt;path&gt;] [-t &lt;threshold&gt;]

Description  
- Scans all `*.h`, `*.cpp`, `*.hpp` files under the target directory.  
- Reports duplicated code sequences at or above the given line count.  
Defaults:  
• `--path` → current working directory  
• `--threshold` → 10 lines  

Parameters  
- `-p, --path <path>`  
  Directory root to scan. If omitted, uses `$(pwd)` or `$GMASH_FIND_DUPLICATE_CODE_PATH`.  
- `-t, --threshold <count>`  
  Minimum matching lines to flag. Defaults to 10 or `$GMASH_FIND_DUPLICATE_CODE_THRESHOLD`.  

Environment Overrides  
- Export `GMASH_FIND_DUPLICATE_CODE_PATH` / `GMASH_FIND_DUPLICATE_CODE_THRESHOLD` to set defaults without CLI flags.  
- ARGV variables (`ARGV_PATH`, `ARGV_THRESHOLD`) take precedence when functions are sourced directly.

Usage Examples  
Standard invocation:  
```bash
gmash find duplicate-code -p /home/alice/projects/lib -t 15
```
→ Scans `/home/alice/projects/lib`, flagging duplicates ≥ 15 lines.

Using environment vars:  
```bash
export GMASH_FIND_DUPLICATE_CODE_PATH=~/workspace/foo
export GMASH_FIND_DUPLICATE_CODE_THRESHOLD=20
gmash find duplicate-code
```
→ Equivalent to `gmash find duplicate-code -p ~/workspace/foo -t 20`.

Direct function call (sourced context):  
```bash
# inside a custom script after sourcing gmash:
gmash_find_duplicate_code "/opt/src" "25"
```

Implementation Snippet  
```bash
gmash_find_duplicate_code(){
  local _path=${ARGV_PATH:-$1}
  local _threshold=${ARGV_THRESHOLD:-$2}
  local _cpp_extensions="./*.h ./*.cpp ./*.hpp"

  [ -z "$_threshold" ] && {
    vecho_info "Defaulting --threshold to 10"
    _threshold=10
  }
  if [ -n "$_path" ]; then
    cd "$_path" || exit
    _path_changed=1
  else
    vecho_info "Defaulting --path to current."
    _path="$(pwd)"
  fi

  vecho_info "--path: $_path   --threshold: $_threshold"
  java -jar /c/lib/simian-4.0.0/simian-4.0.0.jar \
    $_cpp_extensions -threshold="$_threshold" -formatter=plain -language=cpp

  [ -n "$_path_changed" ] && cd - >/dev/null
  vecho_done "Scan complete."
}
```

Practical Tips  
- Ensure Java 8+ is installed and `simian-4.0.0.jar` is accessible at `/c/lib/...`.  
- Use `-formatter=plain` output to pipe into CI logs or custom parsers.  
- Adjust extensions or include/exclude patterns by modifying `_cpp_extensions` or adding Simian options.

---

### Grouping Files by Base Name (`--no-extension`)

Purpose  
When using `gmash gist upload` in “all” mode (`-A, --all`), the `--no-extension` flag groups files sharing the same base name (ignoring extensions) into one gist. Ideal for multi-language modules (e.g., `.cpp` + `.hpp`).

How It Works  
1. Scans each directory passed via `-f`/`--file`.  
2. Builds an associative array `file_map` keyed by basename without extension.  
3. Appends matching files under each key.  
4. Creates one gist per key containing all associated files.

Relevant Snippet from `gist.sh`  
```bash
elif [ "$_noextension" == 1 ]; then
  declare -A file_map
  for folder in "${_files[@]}"; do
    for f in "$folder"/*; do
      base_name=$(basename "$f")
      name_no_ext="${base_name%%.*}"
      file_map["$name_no_ext"]+=$'\n'"$f"
      vecho_action "Mapping gist source: '$f' -> '$name_no_ext'"
    done
  done

  for name_no_ext in "${!file_map[@]}"; do
    vecho_process "Creating gist: $name_no_ext"
    mapfile -t Z_GMASH_GIST_UPLOAD_SINGLE_FILES <<< "${file_map[$name_no_ext]}"
    z_gmash_gist_upload_single \
      "<title>" \
      "$name_no_ext" \
      "<readme>" \
      "<description>" \
      "<clonePath>" \
      "<user>" \
      "<no-readme>" \
      "<no-title>" \
      "<public>"
    vecho_action "Finished gist: $name_no_ext"
    Z_GMASH_GIST_UPLOAD_SINGLE_FILES=()
  done
fi
```

Practical Usage  
Assume two dirs `lib1/` and `lib2/`, each with:
- `foo.cpp`, `foo.hpp`  
- `bar.cpp`, `bar.hpp`

To create one gist per module:
```bash
gmash gist upload \
  -A \
  -e \
  -f lib1 \
  -f lib2 \
  -p ~/gists \
  -n "project-modules" \
  -d "Core modules without extensions"
```
Outcome:
- Gist `foo` with both `.cpp` and `.hpp`, cloned to `~/gists/foo`  
- Gist `bar` likewise

Tips & Edge Cases  
- Files with no dot group under their full name.  
- Same basename in different folders merge into one gist.  
- GMash defaults to secret gists; add `-P/--public` for visibility.  
- Clone dir names after basename (e.g., `~/gists/foo`).

---

### gmash lineage merge

Purpose  
Merge git commits from multiple repositories into one linear history by grafting each project’s first commit onto the previous project’s last commit.

Configuration  
• CURRENT_REPO, OLD1…OLD4 – paths or URLs in chronological order  
• WORKDIR – target directory for merged-history clone  

Key Implementation (`lineage.sh`)  
```bash
gmash_lineage_merge(){
  # 1. Clean slate
  rm -rf "$WORKDIR"
  git clone "$CURRENT_REPO" "$WORKDIR"
  cd "$WORKDIR"

  # 2. Graft helper
  function graft_repo {
    local NAME=$1 URL=$2 PREV_LAST=$3
    git remote add "$NAME" "$URL"
    git fetch "$NAME"

    NEW_FIRST=$(git log "$NAME/master" --reverse --format="%H" | head -n1)
    NEW_LAST=$(git log "$NAME/master" --format="%H" | head -n1)

    if [ -n "$PREV_LAST" ]; then
      git replace --graft "$NEW_FIRST" "$PREV_LAST"
      git filter-repo --replace-refs update-no-add
      git diff "$PREV_LAST" "$NEW_FIRST" || true
    fi
    echo "$NEW_LAST"
  }

  # 3. Chain repos
  LAST=$(graft_repo old1 "$OLD1" "")
  LAST=$(graft_repo old2 "$OLD2" "$LAST")
  LAST=$(graft_repo old3 "$OLD3" "$LAST")
  LAST=$(graft_repo old4 "$OLD4" "$LAST")

  # 4. Graft current onto last old
  FIRST_CURRENT=$(git log main --reverse --format="%H" | head -n1)
  git replace --graft "$FIRST_CURRENT" "$LAST"
  git filter-repo --replace-refs update-no-add
  git diff "$LAST" "$FIRST_CURRENT" || true

  # 5. Inspect
  git log --oneline --graph --decorate --all
}
```

Practical Usage  
1. Install dependencies:  
   • git (≥ 2.8)  
   • git-filter-repo  
2. Set variables and run:  
   ```bash
   export CURRENT_REPO=/home/dev/projects/main.git
   export OLD1=/home/dev/archives/v0.git
   export OLD2=/home/dev/archives/v1.git
   export OLD3=/home/dev/archives/v2.git
   export OLD4=/home/dev/archives/v3.git
   export WORKDIR=./merged-history
   gmash lineage merge
   ```
3. Review `merged-history` for a single, linear commit sequence.  
4. To remove grafts:  
   ```bash
   cd merged-history
   git replace -d <commit-sha>
   git filter-repo --replace-refs clean
   ```

---

### gmash mono patch

Purpose  
Push commits from a monorepo into a Git subtree repo, attempting fast-forward first and falling back to a 3-way sync. Automatically handles conflicts or can open a PR on failure.

Synopsis  
gmash mono patch [--user <owner>] [--remote <alias>] [--branch <mono-branch>] [--tgtuser <owner>] [--tgtbr <subtree-branch>] [--path <subtree-path>] [--all] [--make-pr] [--squash]

Required parameters  
• `--user`, `-u`  GitHub user/org owning both repos  
• `--remote`, `-r`  Git remote alias for the subtree (unless `--all`)  
• `--branch`, `-b`  Source mono branch (defaults to `main`)

Optional parameters  
• `--tgtuser`         Target owner (defaults to `--user`)  
• `--tgtbr`           Target branch in subtree (defaults to `main`)  
• `--path`            Subtree path in mono (defaults to `projects/<remote>`)  
• `--all`             Patch all configured subtrees  
• `--make-pr`         On non-FF conflicts, fork & open a PR  
• `--squash`          Squash mono commits into one before pushing  
• `--tempbr`          Name of temporary sync branch  
• `--tempdir`         Directory for temporary worktree  

Fast-forward workflow  
1. `git subtree pull --prefix=<path> <remote> <tgtbr>`  
2. If new commits are pulled, `git pull && git push` on mono  
3. Compare `HEAD:<path>` vs `<remote>/<tgtbr>`; if no diff, finish

3-way sync workflow on divergence  
1. Create detached worktree in `--tempdir` from mono branch  
2. In worktree:  
   • `git subtree split --prefix=<path> --branch=<tempbr>`  
   • `git checkout <tempbr>`  
   • `git fetch <remote> <tgtbr>`  
   • `git merge <remote>/<tgtbr> --allow-unrelated-histories -m "<merge-msg>"`  
   • `git push <remote> <tempbr>:<tgtbr>`  
3. Back in mono:  
   • `git worktree remove --force <tempdir>`  
   • `git merge -s subtree FETCH_HEAD -m "<sync-msg>"`  
   • `git push`

Examples  

Patch a single subtree “foo” from `main`:  
```bash
cd /path/to/mono-repo
git add . && git commit -am "API fix in foo module"
git push origin main
gmash mono patch \
  --user acpp \
  --remote foo \
  --branch main \
  --tgtbr main \
  --path projects/foo
```

Force a PR on conflicts:  
```bash
gmash mono patch -u acpp -r foo -b feature-x --make-pr
```

Patch every subtree in `.git/config`:  
```bash
gmash mono patch --user acpp --all
```

Practical tips  
• Always commit & push mono changes before running `mono patch`.  
• Use `--squash` to collapse commits into a single subtree update.  
• Inspect `git log <remote>/<tgtbr> --oneline` before patching.  
• On persistent conflicts, rerun with `--make-pr` and resolve via GitHub.

---

### gmash subtree new: Adding a Subtree

Purpose  
Import an external Git repo into your monorepo as a subtree, preserving history and automating branch and remote setup.

Essential Functionality  
- Validates you’re on the target branch (`--tgtbr`, default `main`)  
- Computes defaults:  
  • name ← `--remote`  
  • `--tgtuser` ← `--user`  
  • `--br`,`--tgtbr` ← `main`  
  • `--path` ← `projects/<name>`  
- Locates or creates the subtree repo on GitHub (`gh repo create`)  
- Verifies uniqueness of remote alias, URL and path  
- Runs, in order:  
 1. `git remote add -f <remote> <url>`  
 2. `git subtree add --prefix=<path> <url> <tgtbr>`  
 3. `git subtree pull --prefix=<path> <remote> <tgtbr>`  
 4. `git push`

Command-Line Usage  
```bash
# Minimum required flags:
gmash subtree new \
  --remote foo-box \
  --user SophiaSGS \
  --repo SophiaSGS/monorepo \
  --branch main

# Full invocation with custom target:
gmash subtree new \
  --remote foo-box \
  --name foo_box \
  --path submodules/foo_box \
  --user SophiaSGS \
  --tgtuser MyOrg \
  --branch develop \
  --tgtbr release
```

Under-the-Hood Snippet  
```bash
# 1. Branch guard
[ "$(git rev-parse --abbrev-ref HEAD)" = "release" ] || {
  echo "Error: must be on target branch 'release'" >&2
  exit 1
}

# 2. Create or detect GitHub repo
if ! git ls-remote "https://github.com/MyOrg/foo_box.git" &>/dev/null; then
  gh repo create MyOrg/foo_box --private --add-readme \
    --description "[gmash] Generated subtree foo_box"
fi

# 3. Add remote, subtree and push
git remote add -f foo-box https://github.com/MyOrg/foo_box.git
git subtree add --prefix=submodules/foo_box https://github.com/MyOrg/foo_box.git release
git subtree pull --prefix=submodules/foo_box foo-box release
git push
```

Practical Guidance  
• Install and authenticate GitHub CLI (`gh`) for automatic repo creation.  
• Ensure target `--path` does not exist or is empty and isn’t git-ignored.  
• Use a unique `--remote` alias to avoid collisions.  
• Omit `--url` to let gmash infer or provision the repo; specify explicitly if managed elsewhere.  
• Inspect the merge commit to confirm subtree history preservation.
## Configuration & Environment

gmash uses command-line flags and environment variables to control logging, GitHub authentication, and internal paths. This section covers the global flags, supported environment variables, and key default paths exposed by gmash.

### Global Flags

All gmash commands accept these flags:

• `--verbose`, `-v`  
 Enable verbose logging for the current invocation (equivalent to `GMASH_VERBOSE=1`).  
• `--version`  
 Print version metadata (version, release date, commit hash) and exit.  
• `--help`, `-h`  
 Display command usage and exit.

#### Example

```bash
# Clone a repo with extra debug output
gmash --verbose clone my-org/my-repo

# Check installed gmash version
gmash --version
```

### Environment Variables

Set these variables in your shell to configure gmash globally:

• `GMASH_VERBOSE`  
 When non-zero, gmash prints debug and informational messages via common.sh utilities.  
• `GITHUB_TOKEN` (or `GH_TOKEN`)  
 Your GitHub personal access token. Required for operations on private repos and GitHub API calls.

#### Example

```bash
# Turn on verbose logging by default
export GMASH_VERBOSE=1

# Authenticate all GitHub API requests
export GITHUB_TOKEN=ghp_yourpersonalaccesstoken

# Now run any gmash command without --verbose
gmash clone private-org/secret-repo
```

### Default Paths & Globals

global.sh defines these read-only variables for internal use and scripting extension:

• `GMASH_ROOT`  
 Absolute path to the gmash installation root (one level above `gmash-source`).  
• `GMASH_SOURCE_DIR`  
 `$GMASH_ROOT/gmash-source` – directory containing shared scripts (common.sh, global.sh, etc.).  
• `GMASH_VERSION`, `GMASH_RELEASE_DATE`, `GMASH_COMMIT_HASH`  
 Version metadata injected at build time.

You can inspect or override these if you embed gmash functionality into custom scripts.

#### Inspecting Paths

```bash
# Print the gmash installation root
bash -c 'source /usr/local/bin/gmash && echo $GMASH_ROOT'

# Print the shared scripts directory
bash -c 'source /usr/local/bin/gmash && echo $GMASH_SOURCE_DIR'
```

#### Overriding GMASH_ROOT

```bash
# Point gmash to a custom install location
export GMASH_ROOT="$HOME/.local/share/gmash"
gmash --version
## Development & Contribution Guide

This guide orients new contributors through the gmash codebase: directory structure, command dispatch, parser generation workflow, parser extensions, and external dependencies.

### Project Directory Layout

```
gmash-source/
├── command/             # Top-level and subcommand implementations (e.g. gist.sh, find.sh)
├── def-parser/          # getoptions definition files (one per command group)
├── parser/              # Generated parser functions (gmash_parser_*.sh)
├── parser-extensions.sh # Helper functions to extend getoptions parsers
├── dispatch-parsers.sh  # Central dispatcher (gmash_dispatch_parsers)
└── gmash-compile.sh     # Automates parser compilation via gengetoptions
```

### Modular Command Architecture

`dispatch-parsers.sh` defines the central CLI router:

```bash
gmash_dispatch_parsers(){
  local _cmd=$1; shift
  case $_cmd in
    gist)
      gmash_parser_gist "$@"
      eval "set -- $GMASH_ARGR"
      local _sub=$1; shift
      case $_sub in
        prepare)
          cmd_parser_gist_prepare "$@"; cmd_call_gist_prepare ;;
        clone)
          cmd_parser_gist_clone "$@" ;;
        *)
          echo "$GMASH_DISPATCH_PARSERS_INVALID_SUBCMD"; return 1 ;;
      esac
      ;;
    find)
      gmash_parser_find "$@"; … ;;
    *)
      echo "$GMASH_DISPATCH_PARSERS_INVALID_CMD"; return 1 ;;
  esac
  return 0
}
```

Practical invocation:

```bash
# Clone a gist with ID and output directory
gmash_dispatch_parsers gist clone --id 12345 --output-dir ./mygist
```

To add a new sub-command under `find`, edit its nested `case` in `dispatch-parsers.sh`, add:

```bash
…
find)
  gmash_parser_find "$@"; eval "set -- $GMASH_ARGR"
  local _sub=$1; shift
  case $_sub in
    newsub)
      cmd_parser_find_newsub "$@"; cmd_call_find_newsub ;;
    *)
      echo "$GMASH_DISPATCH_PARSERS_INVALID_SUBCMD"; return 1 ;;
  esac
  ;;
…
```

### Parser Generation Workflow

`gmash-compile.sh` uses `gengetoptions` to transform definition scripts into parser functions.

#### compile_parser Helper

```bash
compile_parser(){
  local _cmd=$1 _sub=$2
  local name=${_cmd:-main}
  [ -n "$_sub" ] && name="${_cmd}_${_sub}"
  local src=${_cmd:-main}
  local out="$GMASH_PARSERS_BIN/$src.sh"
  local redirect=(> "$out")
  [ -n "$_sub" ] && redirect=(>> "$out")
  echo "Compiling parser $name …"
  gengetoptions parser \
    -f "$GMASH_PARSERS_SRC/$src.sh" \
    "gmash_def_parser_$name" \
    "gmash_parser_$name" \
    "${redirect[@]}"
  echo "Done."
}
```

- `-f` points to `def-parser/<command>.sh`.  
- Generates `gmash_def_parser_<name>` and `gmash_parser_<name>`.  
- Main parser overwrites (`>`), sub-parsers append (`>>`).

#### Definition File Conventions

In `gmash-source/def-parser/<command>.sh`:

```bash
#!/bin/bash
source ../parser-extensions.sh

extend_parser
standard_parser_setup gmash_gist_help "Manage GitHub gists" \
  "Usage: gmash gist [options] [args]"
standard_parser_help gmash_gist_help

# Repeatable “array” param
array FILE -f --file init:'FILES=()' var:"<path>" \
  -- "Add a file to the gist (repeatable)"
flag VERBOSE  -v --verbose    "Show verbose output"
param ID      -i --id        "Gist identifier"
disp :usage  -h --help

# Build the parser
eval "$(getoptions parser_definition - "$0")"
```

#### Regenerating Parsers

- Rebuild all parsers:  
  ```bash
  ./gmash-compile.sh
  ```
- Rebuild one command group:
  ```bash
  # In gmash-compile.sh, uncomment:
  compile_parser gist
  compile_parser gist clone
  ```
- Main parser: `compile_parser` with no args → `gmash_parser_main`.

#### Integration in Entry Point

```bash
#!/bin/bash
source parser/main.sh
source parser/gist.sh
# … other parser sources …

gmash_dispatch_parsers "$@"
```

### Parser Extensions (`parser-extensions.sh`)

Provides functions to enrich `getoptions`:

- `extend_parser`  
- `standard_parser_setup <helpFunc> <title> <usage>`  
- `standard_parser_help <helpFunc>`  
- `flag`, `param`, `option`, `array`, `disp`  

Example usage in a custom script:

```bash
#!/bin/bash
source parser-extensions.sh

extend_parser
standard_parser_setup example_help "Example Tool" "Usage: example [options] args"
flag DEBUG -d --debug "Enable debug mode"
array ITEMS -I --item init:'ITEMS=()' var:"<value>" -- "Collect multiple items"
disp :usage -h --help

eval "$(getoptions parser_definition - "$0")" exit 1
parse "$@"
```

### External Dependencies

- **Bash** (POSIX-compatible features)  
- **gengetoptions**: generates parser code from definition files  
- **getoptions**: runtime library shipped with gengetoptions  
- Standard Unix tools (`awk`, `sed`, etc.)  

Ensure `gengetoptions` is installed and on your `PATH` before running `gmash-compile.sh`.
