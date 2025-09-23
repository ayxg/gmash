---
title: "gmash gist clone"
nav_order: 401
parent: "gmash gist"
---

# gmash gist clone

### Usage
`gmash gist clone [[args]...]`

### Brief
Clones a gist to the local filesystem as a git repository.

### Params:
`-u`  `--user  <githubUser>` \
&nbsp;&nbsp;&nbsp;&nbsp;Target Gist GitHub username (owner).

`-s`  `--hash  <gistHash>` \
&nbsp;&nbsp;&nbsp;&nbsp;Hash of the gist to clone. Otherwise clones all gists for the   user.

`-p`  `--path  <clonePath>` \
&nbsp;&nbsp;&nbsp;&nbsp;Path to clone the gist to. Defaults to current if not passed.

`-P`  `--prefix  <prefix>` \
&nbsp;&nbsp;&nbsp;&nbsp;Add a prefix to the cloned gist directory name.

`-n`  `--name  <folderName>` \
&nbsp;&nbsp;&nbsp;&nbsp;Name for the cloned gist directory. Defaults to '[prefix]-[hash]'.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display subcommand version.
