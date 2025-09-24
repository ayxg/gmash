---
title: "gmash gist upload"
nav_order: 406
parent: "gmash gist"
---

# gmash gist upload

### Usage
`gmash gist upload  <<-f <fileOrPath>> [-f <fileOrPath>]...> [-t <titleFile> | -n <name>] [-r <readmeFile>] [-d <description>] [-p <cloneToPath>] [-u <githubUser>] [--no-readme] [--no-title] [-P(--public)] [-A(--all)] [-a(--asone)][-e(--no-extension)] [-l <limit>]`

### Brief
Create gists from given file paths and clone them as a local git
repository. If '--all' is passed, push all files inside dir paths as
separate gists to GitHub. Use '--no-extension' to combine files with the
same base name into one gist. Pass '--as-one' to push each dir's files as
a single gist. Adds a 'title.md' and 'readme.md' by default.

### Required:
`-f`  `--file  <filePath>` \
&nbsp;&nbsp;&nbsp;&nbsp;File(s) to upload to the gist.

### Optional Params:
`-t`  `--title  <titleFile>` \
&nbsp;&nbsp;&nbsp;&nbsp;File to upload as the 'title.md'. Generates a default if not set.

`-n`  `--name  <gistName>` \
&nbsp;&nbsp;&nbsp;&nbsp;Title for the gist. Will set the name of the title file to   '[title].md'. Otherwise, --title file name.

`-r`  `--readme  <readmeFile>` \
&nbsp;&nbsp;&nbsp;&nbsp;File to upload as the 'README.md'. Generates a default if not set.

`-d`  `--desc  <gistDescription>` \
&nbsp;&nbsp;&nbsp;&nbsp;Description for the new gist.

`-p`  `--path  <cloneToPath>` \
&nbsp;&nbsp;&nbsp;&nbsp;Path to clone the gist repository to.

`-u`  `--user  <githubUser>` \
&nbsp;&nbsp;&nbsp;&nbsp;Target Gist GitHub username (owner).

### Optional Flags:
`-N`  `--no-readme` \
&nbsp;&nbsp;&nbsp;&nbsp;Dont generate or add a 'readme.md' file.

`-T`  `--no-title` \
&nbsp;&nbsp;&nbsp;&nbsp;Dont add a 'title.md' file. Implicitly disables 'readme.md' file.   Creates an empty gist.

`-P`  `--public` \
&nbsp;&nbsp;&nbsp;&nbsp;Create a public gist. Default is secret.

### '--all' Mode Flags:
`-A`  `--all` \
&nbsp;&nbsp;&nbsp;&nbsp;Interpret all '-f(--file)' paths as directories and push all files   inside them as separate gists.

`-a`  `--asone` \
&nbsp;&nbsp;&nbsp;&nbsp;Push each dir's files as a single gist.

`-l`  `--limit  <limit>` \
&nbsp;&nbsp;&nbsp;&nbsp;Maximum number of gists to create. Defaults to 100 (in-case of   unintentional overload).

`-e`  `--no-extension` \
&nbsp;&nbsp;&nbsp;&nbsp;Ignore source file extensions when naming gists and grouping gist   sources.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display subcommand version.

### Examples:
Case 1 : Create a gist from one or more files.
``` bash
gmash gist upload -f file1 -f file2 -n 'foo-gist' -d 'description of my gist'
```

Case 2 : Create a separate gist for every file in a path, merge files with the same base name.
Given 'dir1' and 'dir2' contain files 'foo.cpp', 'bar.cpp','foo.hpp', 'bar.hpp' respectively,
2 gists will be created and cloned to dirs: 'foo' and 'bar' relative to '--path'.
``` bash
gmash gist upload -A --no-readme --no-extension
```

Case 3 : Create a separate gist for every directory in a path, merging all files in each dir.
Given 'path1' and 'path2' contain dirs 'foo.', 'bar'. 2 gists will be created and cloned to
dirs: 'foo' and 'bar' relative to '--path'.
``` bash
gmash gist upload -A -a -f path1 -f path2
```
