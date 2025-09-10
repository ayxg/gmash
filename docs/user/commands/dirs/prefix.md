## gmash dirs prefix
`gmash dirs prefix --p <prefix> --P [fileOrFolder]`

Add a prefix to a file or each top-level file in a given directory.

### Parameters
- `-p`, `--prefix <prefix>` 
    : Prefix to add.
- `-P`, `--path [fileOrFolder]` 
    : Path to a file or directory. If given a file, only the single file is prefixed. Defaults to current directory.
- `-r`, `--recursive` 
    : If set and given a directory, will recursively prefix files in all subdirectories.
- `-F`, `--force` 
    : If set, will overwrite files if the prefixed name already exists.
- `-f`, `--filter [pattern]` 
    : If set, will only prefix files matching the given pattern (e.g., `*.txt`).
- `-a`, `--all-paths`
    : If set, directories will be prefixed too. Excluding the given root directory.
- `-n`, `--prepend`
    : If set, and a file already has the given prefix, it wont be renamed.
- `-d`, `--dry-run`
    : Don't apply the results.

### Examples
``` bash
# Add prefix "new_" to all files in the current directory
gmash dirs prefix -p new_

# Add prefix "img_" to all files in the specified directory
gmash dirs prefix -p img_ -P path/to/directory

# Add prefix "doc_" to a specific file
gmash dirs prefix -p doc_ -P path/to/file.txt
```
### See Also
- [gmash dirs](/dirs.md)