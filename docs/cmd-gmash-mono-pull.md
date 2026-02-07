---
title: "gmash mono pull"
nav_order: 703
parent: "gmash mono"
---

# gmash mono pull

### Usage
`gmash mono pull <-r <subtreeRemote>> [-b <subtreeBranch>] [-p <subtreePrefixPath>] [-a]`

### Brief
Pull subtree changes to monorepo.

### Parameters:
`-r`  `--remote  <subtreeRemote>` \
&nbsp;&nbsp;&nbsp;&nbsp;Target subtree remote alias.

`-b`  `--branch  [subtreeBranch]` \
&nbsp;&nbsp;&nbsp;&nbsp;Target subtree branch. Prefer not to specify this and let gmash look it up from metadata.

`-p`  `--prefix  [subtreePrefixPath]` \
&nbsp;&nbsp;&nbsp;&nbsp;Subtree prefix path in the monorepo. Prefer not to specify this and let gmash look it up from metadata.

`-a`  `--all` \
&nbsp;&nbsp;&nbsp;&nbsp;Patch all subtrees based on gmash metadata.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display command group version.
