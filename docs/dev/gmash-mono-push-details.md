# `gmash mono push` impl details

The implementation.
Use case : make change in local parent. Push changes to child.

First, lets overview the advertised api of git subtree.
For example, given a subtree remote called 'foo' targeting branch 'main'.

In theory this ideal set of commands would make sense. But actually it fails.
We just pulled. Yet we are behind? Why?
TODO: answer why when I finnaly understand why.
git push
  > Everything up-to-date
git pull -s subtree foo main
  > * branch            main       -> FETCH_HEAD
  > Already up to date.
git subtree push --prefix=projects/foo foo main
  > git push using:  foo main
  > To https://github.com/SophiaSGS/subtree4.git
  >  ! [rejected] 22d7ddf39497f539ebdd3faef42f735868059c60 -> main (non-fast-forward)
  > error: failed to push some refs to 'https://github.com/SophiaSGS/foo.git'
  > hint: Updates were rejected because the tip of your current branch is behind
  > hint: its remote counterpart. If you want to integrate the remote changes,
  > hint: use 'git pull' before pushing again.
  > hint: See the 'Note about fast-forwards' in 'git push --help' for details.

Another 'option' is to simply --force the parent changes onto the subtree.
But this clearly isn't what we need. This set of commands will erase all
previous commit history of the subtree ,and overwrite with the parent commits
for that subtree.
  git subtree split --prefix=projects/foo --branch=foo-temp
  git push foo foo-temp:main --force
  git branch -D foo-temp
  git subtree push --prefix=projects/foo foo main

And finnaly, I present my 3-way sync push. This seems to be the best method
that I have figured out through brute force testing. Information on the
internet regarding pushing from the parent to child is severely lacking.
Overview :
  1. Commit changes to parent.
  2. Split temp branch from subtree and merge back onto parent.
  3. Resolve conficts, if any.
  4. Fetch and merge the updated subtree.

Its definitley slow - but it gets the job done. Overall, from gathered
info people reccomend either :
  - Using subtrees as view-only from the parent perspective.
  - To avoid subtree push unless necessary.
!!(actually after some testing it seems about as-fast as a subtree push...)

In Detail:
  0. Open git-bash in your root parent repo path.

  1. Commit changes in git-bash and add each changed file manually,
     or directly in Visual Studio which will automate this process.
    git add "projects/foo/new_file2"
    git commit -a -m "Modifiaction" -m "details"
    git push

  2. Create a temp branch from subtree, then merge into main parent
     branch to resolve possible conflicts.
    git subtree split --prefix=projects/foo --branch=foo-update-from-mono
    git checkout foo-update-from-mono
    git merge foo/main --allow-unrelated-histories -m ...
    git push foo foo-update-from-mono:main
    git checkout main
    git branch -D foo-update-from-mono

  3. At this point, the subtree child repo is synced with the parent.
     Last step, is to sync the updated commits from the child,by merging
     them back up to the parent repo.
    git fetch foo main
    git merge -s subtree FETCH_HEAD -m ...
    git push

@note you may get some debug info about the current subtree beforehand
      to assert there are no conflicts...
  git fetch foo
  git log foo/main --oneline

@warning METHOD below is a fake news. subtree does NOT have a push/pull-all
         command.
@note !BAD REFERENCE! Ref:
      https://opensource.com/article/20/5/git-submodules-subtrees