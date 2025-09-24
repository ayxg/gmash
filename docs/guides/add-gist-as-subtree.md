---
title: "`gmash gist` Use Cases"
nav_order: 20
parent: Guides
---

## [0] Use `gmash` to manage github gist repos.

### [0.1] Use Case : Add a gist as a subtree.

To add a single gist as a subtree to any repo. Call `gmash subtree new` passing the gist ULR with an appended `.git`.
Use `--dry-run` with `--verbose` to preview results and check for conflicts, before applying.
``` bash
gmash subtree new -l "https://gist.github.com/$user/$git_hash.git" \
      --p "$subtre_prefix_path" -b $source_branch -B $target_branch \
      -R $remote_name
```

Calling `subtree new` will pull and push to the source remote.
A metadata commit messsage in the parent repo will be genrated:
```
Add 'gist/foo-7fe2c96a925c208f2a248ca76422e405/' from commit
     'd06e02cc36b3c12f1565b3ba759b925a784ee838'
git-subtree-dir: gist/foo-7fe2c96a925c208f2a248ca76422e405
git-subtree-mainline: fb64222
git-subtree-split: d06e02c
```



### [0.2] Use Case : Add all your public gists as a subtrees.
To add multiple gists at once, you can use this basic bash script. This script iterates over an array of names and hashes, adding each one as
as a new subtree. The **key is to keep every gist in a unique path**, to
avoid any duplicate names. By default, `gmash subtree new` denies overwrite. For this script, the path format is : `gist/[name]-[hash]`. You may change it to suit your needs. You can see the result of such an operation in [my gist monorepo](https://github.com/ayzg/gists). Notice that each `revision` in your gist is reflected in as a commit in the monorepo. If you decide to use a `--squashed` commit history, you cannot pull unsquashed commits from that subtree or it will result in a **history mismatch** conflict.

``` bash
#!/bin/bash
_user="your_github_username"
_hashes=(
      # array of the gist hashes you wish to add as subtrees.
)
_names=(
      # array of desired names matching the hashes.
)

for i in "${!_hashes[@]}"; do
    _hash="${_hashes[i]}"
    _name="${_names[i]}"
    echo "Hash: $_hash, Name: $_name"
    gmash subtree new -l "https://gist.github.com/$_user/$_hash.git" \
    --path "gist/$_name-$_hash" -b master -B main -R "$_name-$_hash"
    sleep 2 # Don't overload github api
done
```
