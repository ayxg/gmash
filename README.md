# Git Smash - Git Monorepo Management Toolbox
Bash command line toolbox for monorepo git & github repo management. The core command of `gmash` is `gmash mono` which makes managing repos using subtrees more straightforward. 
The toolbox also features additional utility commands for managing and analyzing git repositories.

## `gmash mono` overview and advantages over raw `git subtree`:
| Gmash Command | Purpose | `git subtree` Equivalent | Advantage
| -- | -- | -- | -- |
| `gmash mono subtree`  | Add new or existing git repo as a subtree. | `git subtree add` | Records subtree metadata for future command reference. Able to create new GitHub repo for subtree with a single command. 
| `gmash mono remove`| Remove a subtree folder and it's remotes | `none`| Ability to revert or remove subtree additions based on stored metadata. Has to be done manually otherwise.
| `gmash mono pull` | Pull updates from subtree remote into the mono repo. | `git subtree pull` | Less user-error prone - only remote name must be specified, subtree metadata is inferred from stored metadata. Able to pull all recorded subtrees with a single command.
| `gmash mono push` | Push updates from the mono repo into a subtree remote. | `git subtree push` | Uses alternative 3-Way Sync strategy to `git subtree push`, avoids redundant `tip of your current branch is behind` error. Less user-error prone - only remote name must be specified, subtree metadata is inferred from stored metadata. Able to push all recorded subtrees with a single command.
| `gmash mono clone` | Clone a mono repo and configure subtree remotes based on metadata.| `none` | Adding subtree remotes has to be done manually when performing a regular `git clone`.
| `gmash mono split` | Split an existing subfolder into a new subtree remote. | `none` | Splitting an existing subfolder otherwise requires multiple `git subtree` commands, initially splitting then re-adding as a new subtree.

## Documentation
### See documentation for installation details and command line reference.
https://ayxg.github.io/gmash/
