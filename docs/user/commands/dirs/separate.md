## gmash dirs separate
`gmash dirs separate [path]`

Separate a directory into its constituent parts.

### Parameters
- `-p`, `--path [path]` 
    : Path to separate files from. Defaults to current.
- `-r`, `--recursive` 
    : If set and given a directory, will recursively extract files in all subdirectories.
- `-F`, `--force` 
    : If set, will overwrite files with the last found, if the name already exists in multiple paths.
- `-f`, `--filter [pattern]` 
    : If set, will only prefix files matching the given pattern (e.g., `*.txt`).
- `-d`, `--dry-run`
    : Don't apply the results.
- `-g`, `--git-merge`
    : If set, upon occurence of a duplicate file : will begin a git merge between the files , and request a conflict resolution.

### Examples
``` bash
# TODO: example
```
### See Also
- [gmash dirs](/dirs.md)
