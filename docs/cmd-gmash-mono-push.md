---
title: "gmash mono push"
nav_order: 704
parent: "gmash mono"
---

# gmash mono push

### Usage
`gmash mono push -r [repo] -b [branch]`

### Brief
Push changes in the mono repo to a sub project's remote.

### Parameters:
`-p`  `--path  <prefixPath>` \
&nbsp;&nbsp;&nbsp;&nbsp;Subtree prefix path in the monorepo.

`-r`  `--remote  <subtreeRemote>` \
&nbsp;&nbsp;&nbsp;&nbsp;Target subtree remote alias.

`-B`  `--tgtbr  <subtreeBranch>` \
&nbsp;&nbsp;&nbsp;&nbsp;Target subtree branch.

`-t`  `--tempbr  <tempBranch>` \
&nbsp;&nbsp;&nbsp;&nbsp;Name of the temp worktree branch to create for the push operation. (Prefer not to set manually)

`-T`  `--tempdir  <tempPath>` \
&nbsp;&nbsp;&nbsp;&nbsp;Path to temp worktree directory to create for the push operation. (Prefer not to set manually)

`-a`  `--all` \
&nbsp;&nbsp;&nbsp;&nbsp;Patch all known subtrees in the mono repo.

`-P`  `--make-pr` \
&nbsp;&nbsp;&nbsp;&nbsp;Make a pull request on GitHub with the patched changes.

`-s`  `--squash` \
&nbsp;&nbsp;&nbsp;&nbsp;Squash strategy when merging subtree changes. Must be consistent with  the previous pull of the subtree.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display command group version.
