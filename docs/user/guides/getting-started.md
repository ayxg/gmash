## Getting Started
Follow these steps to install gmash, compile its parsers, verify your setup, and run your first command.

### Prerequisites
- `git-bash` 
- `gh` (GitHub CLI)
- `getoptions` library (only required if you wish to modify the source files)

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
This produces updated parser source files under `gmash-source/parser/` 
and integrates them into the main dispatcher.
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