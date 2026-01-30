# Git Smash
## Git Monorepo Management Toolbox
Bash command line for monorepo git & github repo management.

## Documentation
https://ayxg.github.io/gmash/

## Command Line Usage
```
Usage: gmash [[global-args]...] <main-command> <sub-command> [[args]...]

Smash keyboard - get git. Bash scripts for high-level git & github repo management.
Call [main-cmd] --help for a list of sub-commands.
Call [main-cmd] [sub-cmd] --help for details of each sub-command.

Globals:
  -V,     --verbose                     Globally enable verbose output.
  -Q,     --quiet                       Globally disable output. !Warning: some command outputs may be suppressed.
  -c,     --config <gmashConfigFile>    Use a gmash argument config file.

Commands:
  dirs                                  High level path/file manipulation and analysis.
    prefix          Add a prefix to each top-level file in a directory.
    same            Get a diff of 2 directories.
    separate        Separate a directory into its constituent parts.
    squash          Squash empty paths in a directory.

  find                                  High level file/repo/code searching and analysis.
    duplicate-code  Find duplicate code across files.
    gits            Find git repositories.
    sources         Find source files.

  gist                                  Manage GitHub Gists with git-like functionality, integrates with 'mono' && 'subtree'.
    prepare         Sets up a new gist with a title.md page with the same name as the target source file(s).
    create          Push all files in a directory as gists to GitHub. Adds a title.md and readme.md by default.
    clone           Clones a gist to the local filesystem.
    recover         Recover a user's gist(s) from GitHub remotes as git repos.
    upload          Upload files to existing gists.

  lineage                               Amalgamate git commits from archived git repos to a more recent version.
  mono                                  Git+GitHub monorepo workflow strategy.
    sub           Add or re-configure a sub project to the mono repo as a subtree.
    pull          Pull changes from a sub project's remote into the mono repo.
    push          Push changes in the mono repo to a sub project's remote.
    config        Configure a mono repo's remotes based on stored subproject metadata.


Display:
  -h,     --help                        Display gmash, command or subcommand help. Use -h or --help.
  -v,     --version                     [v0-0-0] Display gmash, command or subcommand version.
          --versions                    Display versions of gmash and all commands/subcommands.

Development:
    --compile-parser        Compile command line parser source files.
```
