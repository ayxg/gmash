# gmash gist recover

### Usage
`gmash gist recover [[args]...]`

### Brief
Recover a user's gist(s) from GitHub remotes as git repos.

### Params:
`-u`  `--user  <githubUser>` \
&nbsp;&nbsp;&nbsp;&nbsp;Target Gist GitHub username (owner).

`-s`  `--hash  <gistHash>` \
&nbsp;&nbsp;&nbsp;&nbsp;Hash of the gist to recover. Otherwise recovers all gists for the     user.

`-p`  `--path  <recoverPath>` \
&nbsp;&nbsp;&nbsp;&nbsp;Path to recover the gist to. Defaults to current if not passed.

### Flags:
`-s`  `--secret` \
&nbsp;&nbsp;&nbsp;&nbsp;Recover secret gists, only applies when --hash is not specified.

`-P`  `--public` \
&nbsp;&nbsp;&nbsp;&nbsp;Recover public gists, only applies when --hash is not specified.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display subcommand version.
