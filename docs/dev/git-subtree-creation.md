Detailed overview of the git process for creating an example subtree 'foo-box'.
For each submodule:
1. Create github repo with only a single commit (eg. .gitignore or README.md).

2. Create a folder for the submodule inside the monorepo submodules directory.

3. Set up the monorepo for a subtree merge.
    1. Open "git-bash" console in the local monorepo folder.

    2. Add a new remote URL pointing to the separate submodule repo that was
    created on step 1.
    git remote add -f foo-box https://github.com/SophiaSGS/foo-box.git
    Updating foo-box
    remote: Enumerating objects: 3, done.
    remote: Counting objects: 100% (3/3), done.
    remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
    Unpacking objects: 100% (3/3), 869 bytes | 8.00 KiB/s, done.
    From https://github.com/SophiaSGS/foo-box
    * [new branch]      main       -> foo-box/main

    3. Merge the submodule repo into the monorepo. This doesn't change any of
    your files locally, but it does prepare Git for the next step.
    You must also indicate which specific branch you wish to merge. In this
    case 'main'.
        git merge -s ours --no-commit --allow-unrelated-histories foo-box/main
    Automatic merge went well; stopped before committing as requested

    4. Create a folder for the submodule inside the monorepo submodules directory.
    Then, copy the Git history of the submodule project into it using
    'read-tree'. '--prefix' is the path inside the monorepo where the module
    will be stored. You must also specify the branch argument '-u'.
            "Not a fatal error? false positive."
        git read-tree --prefix=boxes/foo_box/ -u foo-box/main
        fatal: refusing to merge unrelated histories

    5. Commit the submodule subtree changes locally.
    git commit -m "Merged submodule subtree 'foo-box' into monorepo 'boxes/foo_box'."
    [main fe0ca25] Merged submodule subtree 'foo-box' into monorepo 'boxes/foo_box'.

    6. Push the monorepo's submodule tree changes to the remote GitHub monorepo
    from the git-bash.
        git push