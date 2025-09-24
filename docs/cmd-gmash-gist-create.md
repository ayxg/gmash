---
title: "gmash gist create"
nav_order: 402
parent: "gmash gist"
---

# gmash gist create

### Usage
`gmash gist create [<-f <file>>...] [-t [titleFile] | -n [name]]   [-r [readmeFile]] [-d [description]] [--no-readme] [--no-title]   [-p(--public)]`

### Brief
Push given files as gists to GitHub. Adds a title.md   and readme.md by default.

### Params:
`-f`  `--file  <filePath>` \
&nbsp;&nbsp;&nbsp;&nbsp;File(s) to upload to the gist.

`-t`  `--title  <titleFile>` \
&nbsp;&nbsp;&nbsp;&nbsp;File to upload as the 'title.md'. Generates a default if not set.

`-n`  `--name  <gistName>` \
&nbsp;&nbsp;&nbsp;&nbsp;Title for the gist. Will set the name of the title file to   '[title].md'. Otherwise, --title file name.

`-r`  `--readme  <readmeFile>` \
&nbsp;&nbsp;&nbsp;&nbsp;File to upload as the 'README.md'. Generates a default if not set.

`-d`  `--desc  <gistDescription>` \
&nbsp;&nbsp;&nbsp;&nbsp;Description for the new gist.

### Flags:
`--no-readme` \
&nbsp;&nbsp;&nbsp;&nbsp;Don't generate or add a 'readme.md' file.

`--no-title` \
&nbsp;&nbsp;&nbsp;&nbsp;Don't add a 'title.md' file. Implicitly disables 'readme.md' file. Creates an empty gist.

`-p`  `--public` \
&nbsp;&nbsp;&nbsp;&nbsp;Create a public gist. Default is secret.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display subcommand version.
