---
title: "gmash gist prepare"
nav_order: 403
parent: "gmash gist"
---

# gmash gist prepare

### Usage
`gmash gist prepare [-t [titleFile] | -n [name]] [-r [readmeFile]] [-d [description]] [--no-readme] [--no-title] [-p(--public)]`

### Brief
Sets up an empty gist with a 'title.md' and 'readme.md' file.

### Params:
`-t`  `--title  <titleFile>` \
&nbsp;&nbsp;&nbsp;&nbsp;File to upload as the 'title.md'. Generates a default if not set.

`-n`  `--name  <gistName>` \
&nbsp;&nbsp;&nbsp;&nbsp;Title for the gist. Will set the name of the title file to '[title].md'. Otherwise, --title file name.

`-r`  `--readme  <readmeFile>` \
&nbsp;&nbsp;&nbsp;&nbsp;File to upload as the 'README.md'. Generates a default if not set.

`-d`  `--desc  <gistDescription>` \
&nbsp;&nbsp;&nbsp;&nbsp;Description for the new gist.

### Flags:
`-N`  `--no-readme` \
&nbsp;&nbsp;&nbsp;&nbsp;Dont generate or add a 'readme.md' file.

`-T`  `--no-title` \
&nbsp;&nbsp;&nbsp;&nbsp;Dont add a 'title.md' file. Implicitly disables 'readme.md' file. Creates an empty gist.

`-P`  `--public` \
&nbsp;&nbsp;&nbsp;&nbsp;Create a public gist. Default is secret.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display subcommand version.
