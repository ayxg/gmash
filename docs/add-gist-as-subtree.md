# Use Case : Add a gist as a subtree.

``` bash
$ gmash -V subtree new -l "https://gist.github.com/zhymet/7fe2c96a925c208f2a248ca76422e405.git" --path "gist/util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405" -b master -B main -R util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405
```

```
 gmash->new->subtree
    ⚙  Verifying parameters.
          ✓  Params verified, working on mono branch 'gists/main'.
    ⓘ  Final input parameters:
    --remote='util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405',
    --path='gist/util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405',
    --url='https://gist.github.com/zhymet/7fe2c96a925c208f2a248ca76422e405.git',
    --user='{currentGithubUser}',
    --tgtuser='{currentGithubUser}',
    --br='master',
    --tgtbr='main',
    --name='subtreeDirName'.
    ⚙  Getting/Creating target subtree repo.
          ✓  Target subtree repo URL: 'https://gist.github.com/zhymet/7fe2c96a925c208f2a248ca76422e405.git' ready for subtree remote 'util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405'.
Guarding current remotes, subtrees and mono paths. Overwrite disabled.
        ->  Remote 'util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405' is unique.
        ->  URL 'https://gist.github.com/zhymet/7fe2c96a925c208f2a248ca76422e405.git' is not used by any existing remote.
        ->  Target path 'gist/util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405' is clear.
        ->  Target path 'gist/util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405' is not ignored by gitignore.
          ✓  Safe to add subtree.
 git remote add -f 'util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405' 'https://gist.github.com/zhymet/7fe2c96a925c208f2a248ca76422e405.git'
Updating util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405
From https://gist.github.com/zhymet/7fe2c96a925c208f2a248ca76422e405
 * [new branch]      main       -> util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405/main
 git subtree add --prefix='gist/util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405' 'util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405' 'main'
git fetch https://gist.github.com/zhymet/7fe2c96a925c208f2a248ca76422e405.git main
From https://gist.github.com/zhymet/7fe2c96a925c208f2a248ca76422e405
 * branch            main       -> FETCH_HEAD
Added dir 'gist/util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405'
 git subtree pull --prefix='gist/util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405' 'util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405' 'main'
From https://gist.github.com/zhymet/7fe2c96a925c208f2a248ca76422e405
 * branch            main       -> FETCH_HEAD
Already up to date.
 git push
Enumerating objects: 7, done.
Counting objects: 100% (7/7), done.
Delta compression using up to 8 threads
Compressing objects: 100% (5/5), done.
Writing objects: 100% (6/6), 1.54 KiB | 1.54 MiB/s, done.
Total 6 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To https://github.com/ayzg/gists.git
   fb64222..4383a8e  master -> master
          ✓  Subtree 'util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405' added to 'gist/util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405' and pushed to remote.
    ⓘ  Result metadata:      [Remote URL]: 'https://gist.github.com/zhymet/7fe2c96a925c208f2a248ca76422e405.git'
      [Target Remote Alias]: 'util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405'
      [Target Subtree Branch]: 'main'
      [Mono Repo]: '{currentGithubUser}/gists'
      [Subtree Repo]: '{currentGithubUser}/subtreeDirName'
      [Mono->Subtree Link Path]: 'gist/util-cxx20-contig-enum-7fe2c96a925c208f2a248ca76422e405'.

```