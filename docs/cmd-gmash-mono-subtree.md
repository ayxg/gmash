---
title: "gmash mono subtree"
nav_order: 701
parent: "gmash mono"
---

# gmash mono subtree

### Usage
`gmash mono subtree <-p <subtreePrefixPath>> <-r <remoteAlias>> <-l <remoteUrl>> <-b <subtreeBranch>> [-n] [-N <subtreeRepoName>] [-O <subtreeRepoOwner>] [-s]`

### Brief
Add or re-configure a sub project to the mono repo as a subtree.

### Parameters:
`-p`  `--prefix  <subtreePrefixPath>` \
&nbsp;&nbsp;&nbsp;&nbsp;Relative path inside the parent repo where the subtree will be added. Cannot be the root path. The path must be empty or non-existent in the parent repo. gmash will deny adding a subtree to a path which already contains any files.

`-r`  `--remote  <remoteAlias>` \
&nbsp;&nbsp;&nbsp;&nbsp;Remote alias to add to the parent repo, which will be refered to when pulling and pushing changes to the added subtree.

`-l`  `--url  <remoteURL>` \
&nbsp;&nbsp;&nbsp;&nbsp;Remote repository URL of the subtree to add. Ignored if '--new' is passed.

`-b`  `--branch  <subtreeBranch>` \
&nbsp;&nbsp;&nbsp;&nbsp;Target branch of the subtree remote to pull in.

`-s`  `--squash` \
&nbsp;&nbsp;&nbsp;&nbsp;Instead of merging the entire history from the subtree project, produce only a single commit that contains all the differences to merge. Then, merge that new commit into the parent repo. Note, if you add a subtree with --squash, future

### pulls and pushes to that subtree should also be squashed.
`-n`  `--new` \
&nbsp;&nbsp;&nbsp;&nbsp;Create a new github repo for the added subtree. Requires '--name' and '--owner' to be specified.

`-N`  `--name  <subtreeRepoName>` \
&nbsp;&nbsp;&nbsp;&nbsp;Name of the new remote repo to create for the subtree. Required if '--new' is passed.

`-O`  `--owner  <subtreeRepoOwner>` \
&nbsp;&nbsp;&nbsp;&nbsp;Owner (user or org) of the new remote repo to create for the subtree. Required if '--new' is passed.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display command group version.
