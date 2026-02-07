---
title: "gmash mono subtree"
nav_order: 706
parent: "gmash mono"
---

# gmash mono subtree

### Usage
`gmash mono subtree <-p <subtreePrefixPath>> <-r <remoteAlias>> [-l <remoteUrl>] <-b <subtreeBranch>> [-N <subtreeRepoName>] [-O <subtreeRepoOwner>] [-s]`

### Brief
Split a prefix path into a new subtree remote repo, and re-add it as a subtree in this repo.

### Parameters:
`-p`  `--prefix  <subtreePrefixPath>` \
&nbsp;&nbsp;&nbsp;&nbsp;Relative path inside the parent repo where the subtree will be split from. Cannot be the root path.

`-r`  `--remote  <remoteAlias>` \
&nbsp;&nbsp;&nbsp;&nbsp;Remote alias to add to the parent repo, which will be refered to when pulling and pushing changes to the added subtree.

`-l`  `--url  <remoteURL>` \
&nbsp;&nbsp;&nbsp;&nbsp;Remote repository URL of the subtree to add. New github repo won't be created if url is specified.

`-b`  `--branch  <subtreeBranch>` \
&nbsp;&nbsp;&nbsp;&nbsp;Target branch of the subtree remote.

`-s`  `--squash` \
&nbsp;&nbsp;&nbsp;&nbsp;Instead of merging the entire history from the subtree project, produce only a single commit that contains all the differences to merge. Then, merge that new commit into the parent repo. Note, if you add a subtree with --squash, future

### pulls and pushes to that subtree should also be squashed.
`-N`  `--name  <subtreeRepoName>` \
&nbsp;&nbsp;&nbsp;&nbsp;Name of the new remote repo to create for the subtree. Required if '--url' is not passed.

`-O`  `--owner  <subtreeRepoOwner>` \
&nbsp;&nbsp;&nbsp;&nbsp;Owner (user or org) of the new remote repo to create for the subtree. Required if '--url' is not passed.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display command group version.
