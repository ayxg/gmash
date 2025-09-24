---
title: "gmash dirs prefix"
nav_order: 201
parent: "gmash dirs"
---

# gmash dirs prefix

### Usage
`gmash dirs prefix --p <prefix> --P [fileOrFolder]`

### Brief
Add a prefix to each top-level file in a directory. If no path is provided, uses current directory.
If given a file path, only the single file is prefixed.
Overwrite is denied if the resulting prefixed name already exists in the directory.

### Parameters:
`-p`  `--prefix  <prefix>` \
&nbsp;&nbsp;&nbsp;&nbsp;Prefix to add.

`-P`  `--path  [fileOrFolder]` \
&nbsp;&nbsp;&nbsp;&nbsp;Path to a file or directory. If given a file, only the single file is prefixed.

### Display:
`-h`  `--help` \
&nbsp;&nbsp;&nbsp;&nbsp;Display gmash, command or subcommand help. Use -h or --help.

`-v`  `--version  [v0-0-0]` \
&nbsp;&nbsp;&nbsp;&nbsp;Display command group version.
