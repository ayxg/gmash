# Git Smash - Git Monorepo Management Toolbox
### Bash command line toolbox for monorepo git & github repo management. 

#### The core command of `gmash` is `gmash mono` which makes managing repos using subtrees more straightforward. 

A brief overview of the advantages compared to raw `git subtree`:
- `gmash mono subtree`: Will add an existing or create a new repo as a subtree while also recording the subtree's metadata in a `.gmash` folder.
- `gmash mono remove` : Removes a subtree, it's metadata and related remotes from the parent repo.
- `gmash mono pull|push` : Pulling and pushing from a created subtree only requires the remote name to be specified. 
- You are also able to pull or push from **all** recorded subtrees automatically by passing an `--all` argument to `mono pull|push`.
- `gmash mono push` : Uses a diffrent merge strategy and avoids annoying edge cases compared to `git subtree push`.
- `gmash mono clone` : Clones a monorepo and automatically sets up the subtree remotes based on metadata. This has to be done manually upon a regular clone otherwise.

## Documentation
### See documentation for installation details and command line reference.
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
  dirs                                  High level path/file manipulation.
    prefix          Add a prefix to each top-level file in a directory.
    same            Get a diff of 2 directories.
    separate        Separate a directory into its constituent parts.
    squash          Squash empty paths in a directory.

  find                                  High level file/repo/code searching and analysis.
    duplicate-code  Find duplicate code across files.
    gits            Find git repositories.
    sources         Find source files.

  gist                                  Manage GitHub Gists with git-like functionality, integrates with 'mono' command.
    prepare         Sets up a new gist with a title.md page with the same name as the target source file(s).
    create          Push all files in a directory as gists to GitHub. Adds a title.md and readme.md by default.
    clone           Clones a gist to the local filesystem.
    recover         Recover a user's gist(s) from GitHub remotes as git repos.
    upload          Upload files to existing gists.

  lineage                               Prepend git commits from archived git repos to a more recent version.
  mono                                  Git subtree monorepo workflow strategy.
    subtree       Add or re-configure a sub project to the mono repo as a subtree.
    remove        Add or re-configure a sub project to the mono repo as a subtree.
    pull          Pull changes from a sub project's remote into the mono repo.
    push          Push changes in the mono repo to a sub project's remote.
    clone         Clone and configure a mono repo's remotes based on stored subproject metadata.


Display:
  -h,     --help                        Display gmash, command or subcommand help. Use -h or --help.
  -v,     --version                     [v0-0-0] Display gmash, command or subcommand version.
          --versions                    Display versions of gmash and all commands/subcommands.

Development:
    --compile-parser        Compile command line parser source files.
    --unit-tests            Run unit test to validate program.
```
