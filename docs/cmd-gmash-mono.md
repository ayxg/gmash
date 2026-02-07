---
title: "gmash mono"
nav_order: 700
parent: "gmash"
---

# gmash mono

### Usage
`gmash mono <sub-command> [[args]...]`

### Brief
Git+GitHub monorepo workflow strategy.
Call [main-cmd] [sub-cmd] --help for details of each sub-command.

### Commands

`subtree` \
&nbsp;&nbsp;&nbsp;&nbsp;Add or re-configure a sub project to the mono repo as a subtree.

`remove` \
&nbsp;&nbsp;&nbsp;&nbsp;Remove a subtree from the monorepo.

`pull` \
&nbsp;&nbsp;&nbsp;&nbsp;Pull changes from a sub project's remote into the mono repo.

`push` \
&nbsp;&nbsp;&nbsp;&nbsp;Push changes in the mono repo to a sub project's remote.

`config` \
&nbsp;&nbsp;&nbsp;&nbsp;Configure a mono repo's remotes based on stored subproject metadata.

`clone` \
&nbsp;&nbsp;&nbsp;&nbsp;Clone repo from remote or local and add subtrees based on stored metadata.

`split` \
&nbsp;&nbsp;&nbsp;&nbsp;Split an existing prefix path into a new subtree.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display command group version.
