---
title: "gmash mono remove"
nav_order: 702
parent: "gmash mono"
---

# gmash mono remove

### Usage
`gmash mono remove <-r <subtreeRemote>> [-p <subtreePrefixPath>] [-k]`

### Brief
Remove a subtree from the monorepo.

### Parameters:
`-r`  `--remote  <subtreeRemote>` \
&nbsp;&nbsp;&nbsp;&nbsp;Target subtree remote alias.

`-p`  `--prefix  <subtreePrefixPath>` \
&nbsp;&nbsp;&nbsp;&nbsp;Subtree prefix path in the monorepo. Prefer not to specify this and let gmash look it up from metadata.

`-k`  `--keep-remote` \
&nbsp;&nbsp;&nbsp;&nbsp;Keep the remote alias in the parent repo even if it is no longer used.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display command group version.
