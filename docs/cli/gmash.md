# gmash

### Usage
`gmash [[global-args]...] <main-command> <sub-command> [[args]...]`

### Commands

`dirs` \
&nbsp;&nbsp;&nbsp;&nbsp;High level path/file manipulation and analysis.\
&nbsp;&nbsp;&nbsp;&nbsp;`same`\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Get a diff of 2 directories.\
&nbsp;&nbsp;&nbsp;&nbsp;`separate`\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Separate a directory into its constituent parts.\
&nbsp;&nbsp;&nbsp;&nbsp;`squash`\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Squash empty paths in a directory.

`find` \
&nbsp;&nbsp;&nbsp;&nbsp;High level file/repo/code searching and analysis.\
&nbsp;&nbsp;&nbsp;&nbsp;`gits`\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Find git repositories.\
&nbsp;&nbsp;&nbsp;&nbsp;`sources`\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Find source files.

`gist` \
&nbsp;&nbsp;&nbsp;&nbsp;Manage GitHub Gists with git-like functionality, integrates with 'mono' && 'subtree'.\
&nbsp;&nbsp;&nbsp;&nbsp;`create`\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Push all files in a directory as gists to GitHub. Adds a title.md and readme.md by default.\
&nbsp;&nbsp;&nbsp;&nbsp;`clone`\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Clones a gist to the local filesystem.\
&nbsp;&nbsp;&nbsp;&nbsp;`recover`\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Recover a user's gist(s) from GitHub remotes as git repos.\
&nbsp;&nbsp;&nbsp;&nbsp;`upload`\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Upload files to existing gists.

`lineage` \
&nbsp;&nbsp;&nbsp;&nbsp;Amalgamate git commits from archived git repos to a more recent version.

`mono` \
&nbsp;&nbsp;&nbsp;&nbsp;Manage Monorepo->Subtree github git remotes and locals.

`subtree` \
&nbsp;&nbsp;&nbsp;&nbsp;Manage Subtree->Monorepo github git remotes and locals.

### Globals:
`-V`  `--verbose` \
&nbsp;&nbsp;&nbsp;&nbsp;Globally enable verbose output.

`-Q`  `--quiet` \
&nbsp;&nbsp;&nbsp;&nbsp;Globally disable output. !Warning: some command outputs may be suppressed.

`-c`  `--config  <gmashConfigFile>` \
&nbsp;&nbsp;&nbsp;&nbsp;Use a gmash argument config file.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand version.

`--versions` \
&nbsp;&nbsp;&nbsp;&nbsp;Display versions of gmash and all commands/subcommands.

### Development:
`--compile-parser` \
&nbsp;&nbsp;&nbsp;&nbsp;Compile command line parser source files.
