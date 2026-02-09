# Mono-Subtree Workflow


## `mono split` : Creating a new subtree from and existing mono subdirectory.
`mono split` can be used to split an existing subdirectory into a new subtree remote. Implicitly, this must be an `owned` remote which the mono
repo can push to. The split can be directed at subtree's the upstream branch, but the recommended procedure is to have a permanent side branch(`mono`)
which acts as a `push/pull` channel to the parent repo. The split operation will **force push** the split commit history into the target remote,
**do not** apply a split to the upstream branch of a non-empty existing repo.

#### Case 1: Split into a pre-existing remote.
Example split into a pre-existing remote which may be local or on a server. When splitting into an existing remote and not specifying the
upstream as the target branch, you must manually overwrite the upstream with the targeted branch. If the target remote contains code on
the upstream branch you desire to merge with the split subtree history, you must perform a merge with `--allow-unrelated-histories`.

``` bash
# Split "project/project1" into a local remote "/c/my/local/project1.git".

# gmash mono split --remote project1 --prefix project/project1 --branch mono --url /c/my/local/project1.git
cd parent_repo
gmash mono split -r project1 -p projects/project1 -b mono -l /c/my/local/project1.git


# Manually overwrite the upstream in the subtree.
cd ..
git clone /c/my/local/project1.git
cd project1
git pull
git checkout master
git reset --hard origin/mono
git push --force

# OR

# If it's not a fresh repo and you desire to merge changes you must merge unrelated histories.
cd ..
git clone /c/my/local/project1.git
cd project1
git pull
git checkout master
git merge mono --allow-unrelated-histories
git push --force

```

#### Case 2: Split into a new GitHub repo.
Example split into a new GitHub repo which will be created by gmash through `gh`. Unlike `Case 1`, gmash will overwrite the upstream
branch to match the given target branch after creating and pushing to the new GitHub repo. Note that in this case the `--url` argument
must be ommited. Instead the target repo `--name` and `--owner` must be provided to specify the GitHub repo creation target.

``` bash
# gmash mono split --remote project1 --prefix project/project1 --branch mono --name project1 --owner gh_username
gmash mono split -r project1 -p project/project1 -b mono -N project1 -O gh_username
```