---
title: "gmash gist"
nav_order: 400
parent: "gmash"
---

# gmash gist

### Usage
`gmash gist <sub-command> [[args]...]`

### Commands

`prepare` \
&nbsp;&nbsp;&nbsp;&nbsp;Sets up a new gist with a title.md page with the same name as the   target source file(s).

`create` \
&nbsp;&nbsp;&nbsp;&nbsp;Push given files as gists to GitHub. Adds a title.md   and readme.md by default.

`clone` \
&nbsp;&nbsp;&nbsp;&nbsp;Clones a gist to the local filesystem.

`recover` \
&nbsp;&nbsp;&nbsp;&nbsp;Recover a user's gist(s) from GitHub remotes as git repos.

`upload` \
&nbsp;&nbsp;&nbsp;&nbsp;Create gists from a set of files or folders and clone them back asgit repos.

### Manage GitHub Gists with git-like functionality.
Use 'upload' to create gists from local files and clone them back as git   repos.
Use 'recover' to create mono-subtree repo from a set of selected gists.
Use 'gmash mono' and 'gmash subtree' command groups for management of the  gist mono-repo.
Use 'prepare','create' and 'clone' for lower level control. See sub-command  help for details.

### Globals:
`-u`  `--user  <githubUser>` \
&nbsp;&nbsp;&nbsp;&nbsp;Global gist source(  owner) github user.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display command group version.
