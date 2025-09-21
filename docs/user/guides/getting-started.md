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
**Only necessary IF you changed the parser definition source code**
Requires `getoptions` shell library.
```bash
gmash --compile-parser
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
$ gmash --help
gmash v0-0-0
AGPL-3.0-or-later Copyright(c) 2025 Anton Yashchenko
Smash keyboard - get git. Bash scripts for high-level git & github repo management.

Usage: gmash [[global-args]...] <main-command> <sub-command> [[args]...]

Globals:
          --verbose                     Globally enable verbose output.
          --quiet                       Globally disable output. !Warning: some command outputs may be suppressed.
          --config <gmashConfigFile>    Use a gmash argument config file.

Commands:
  dirs                                  High level path/file manipulation and analysis.
        prefix           -- Add a prefix to each top-level file in a directory.
        same             -- Get a diff of 2 directories.
        separate         -- Separate a directory into its constituent parts.
        squash           -- Squash empty paths in a directory.

  find                                  High level file/repo/code searching and analysis.
        duplicate-code   -- Find duplicate code across files.
        gits             -- Find git repositories.
        sources          -- Find source files.

  gist                                  Manage GitHub Gists with git-like functionality, integrates with 'mono' && 'subtree'.
        prepare          -- Sets up a new gist with a title.md page with the same name as the target source file(s).
        create           -- Push all files in a directory as gists to GitHub. Adds a title.md and readme.md by default.
        clone            -- Clones a gist to the local filesystem.
        recover          -- Recover a user's gist(s) from GitHub remotes as git repos.
        upload           -- Upload files to existing gists.

  lineage                               Amalgamate git commits from archived git repos to a more recent version.
  mono                                  Manage Monorepo->Subtree github git remotes and locals.
  subtree                               Manage Subtree->Monorepo github git remotes and locals.

Display:
  -h,     --help                        Display gmash, command or subcommand help. Use -h or --help.
  -v,     --version                     [v0-0-0] Display gmash, command or subcommand version.
  -V,     --versions                    Display versions of gmash and all commands/subcommands.

```
