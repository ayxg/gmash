#!/bin/bash
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Unit test globals
GMASH_UNIT_TEST_SEPARATOR="==================================================================
=================================================================="
GMASH_BINARY_PATH=""           # Path to gmash binary.
GMASH_TEST_TEMPDIR=""          # Temp directory for tests.
GMASH_TEST_SUBREPO_DIR=""      # Test local sub-repo directory.
GMASH_TEST_MONOREPO_DIR=""     # Test local monorepo directory.
GMASH_TEST_SUBREPO_BARE=""     # Test bare repo used as remote for the subrepo.
GMASH_TEST_MONOREPO_BARE=""    # Test bare repo used as remote for the monorepo
GMASH_TEST_MONO_SUBREPO_PREFIX="" # Subrepo prefix path in the monorepo.
GMASH_TEST_MONO_SUBREPO_REMOTE="" # Subrepo remote name in the monorepo.

configure_testbed(){
    # Init global paths
    GMASH_BINARY_PATH="$_SCRIPT_DIR/../gmash" # 'gmash-test' is relative to gmash root
    GMASH_TEST_TEMPDIR="$(mktemp --tmpdir -d "gmash-unit-tests-XXXX")"
    GMASH_TEST_SUBREPO_DIR="$GMASH_TEST_TEMPDIR/subrepo"
    GMASH_TEST_MONOREPO_DIR="$GMASH_TEST_TEMPDIR/monorepo"
    GMASH_TEST_SUBREPO_BARE="$GMASH_TEST_TEMPDIR/subrepo_remote.git"
    GMASH_TEST_MONOREPO_BARE="$GMASH_TEST_TEMPDIR/monorepo_remote.git"
    GMASH_TEST_MONO_SUBREPO_PREFIX="project1"
    GMASH_TEST_MONO_SUBREPO_REMOTE="project1_origin"

    echo "$GMASH_UNIT_TEST_SEPARATOR"
    echo "Configured testbed"
    echo "$GMASH_UNIT_TEST_SEPARATOR"

    echo "  GMASH_BINARY_PATH:        $GMASH_BINARY_PATH"
    echo "  GMASH_TEST_TEMPDIR:       $GMASH_TEST_TEMPDIR"
    echo "  GMASH_TEST_SUBREPO_DIR:   $GMASH_TEST_SUBREPO_DIR"
    echo "  GMASH_TEST_MONOREPO_DIR:  $GMASH_TEST_MONOREPO_DIR"
    echo "  GMASH_TEST_SUBREPO_BARE:  $GMASH_TEST_SUBREPO_BARE"
    echo "  GMASH_TEST_MONOREPO_BARE: $GMASH_TEST_MONOREPO_BARE"

    # Switching to test temp dir not to mangle current repo.
    cd "$GMASH_TEST_TEMPDIR" || exit 1
}

cleanup_testbed(){
    echo "Cleaning up testbed at: $GMASH_TEST_TEMPDIR"
    rm -rf "$GMASH_TEST_TEMPDIR"
}
# Cleanup testbed on any script exit.
trap cleanup_testbed EXIT INT TERM

refresh_testbed(){
    echo "Refreshing testbed at: $GMASH_TEST_TEMPDIR"
    rm -rf "$GMASH_TEST_TEMPDIR" && mkdir -p "$GMASH_TEST_TEMPDIR"
}

configure_test_repo_with_local_remote(){
    local _local_path="$1"
    local _remote_path="$2"
    echo "Configuring test repo: local='$_local_path', remote='$_remote_path'"

    # Bare local remote setup
    mkdir -p "$_remote_path"
    git -C "$_remote_path" init --bare -b main > /dev/null 2>&1

    # Local repo setup
    mkdir -p "$_local_path"
    git -C "$_local_path" init -b main > /dev/null 2>&1
    git -C "$_local_path" config core.autocrlf false
    echo "Initial data" > "$_local_path/data.txt"
    git -C "$_local_path" config user.email "test@test.com" # user msut be configured for commits
    git -C "$_local_path" config user.name "Tester"
    git -C "$_local_path" add . && git -C "$_local_path" commit -m "Initial commit" > /dev/null 2>&1
    git -C "$_local_path" remote add origin "$_remote_path"
    git -C "$_local_path" push -u origin main > /dev/null 2>&1
}

ut_gmash_mono_sub(){
    echo "$GMASH_UNIT_TEST_SEPARATOR"
    echo "[UNIT TEST] gmash_mono_sub"
    echo "$GMASH_UNIT_TEST_SEPARATOR"

    # Change into monorepo dir.
    cd "$GMASH_TEST_MONOREPO_DIR" || return 1

    # Run gmash mono sub command.
    "$GMASH_BINARY_PATH" mono sub -p "$GMASH_TEST_MONO_SUBREPO_PREFIX" -r "$GMASH_TEST_MONO_SUBREPO_REMOTE" -l "$GMASH_TEST_SUBREPO_BARE" -b "main" > /dev/null

    # Return code must be 0.
    local result_=$?
    if [ $result_ -ne 0 ]; then
        echo "gmash mono sub command failed with exit code $result_"
        return 1
    fi

    # Verify that the subrepo folder was created in the monorepo.
    if [ ! -d "$GMASH_TEST_MONO_SUBREPO_PREFIX" ]; then
        echo "Subrepo directory '$GMASH_TEST_MONO_SUBREPO_PREFIX' was not created in the monorepo."
        return 1
    fi

    # Verify that the subrepo remote is set correctly.
    local subrepo_remote
    subrepo_remote="$(git -C "$GMASH_TEST_MONOREPO_DIR" remote get-url "$GMASH_TEST_MONO_SUBREPO_REMOTE" 2>/dev/null)"
    if [ -z "$subrepo_remote" ]; then
        echo "Subrepo remote '$GMASH_TEST_MONO_SUBREPO_REMOTE' was not set correctly."
        return 1
    fi

    # Verify that the subrepo remote URL matches the expected local subrepo path.
    if [ "$subrepo_remote" != "$(cygpath -m "$GMASH_TEST_SUBREPO_BARE")" ]; then # git returns normalized windows path
        echo "Subrepo remote URL '$subrepo_remote' does not match expected '$(cygpath -m "$GMASH_TEST_SUBREPO_BARE")'."
        return 1
    fi

    # Check that metadata file was created .gmash/subtree/project1_origin.conf
    if [ ! -f "$GMASH_TEST_MONOREPO_DIR/.gmash/subtree/$GMASH_TEST_MONO_SUBREPO_REMOTE.conf" ]; then
        echo "Metadata file '$GMASH_TEST_MONOREPO_DIR/.gmash/subtree/$GMASH_TEST_MONO_SUBREPO_REMOTE.conf' was not created."
        return 1
    fi

    # Ensure metadata file contains correct info.
    local metadata_file="$GMASH_TEST_MONOREPO_DIR/.gmash/subtree/$GMASH_TEST_MONO_SUBREPO_REMOTE.conf"

    # URL line check.
    local url_line
    url_line=$(grep "^url=" "$metadata_file")
    if [ "$url_line" != "url=$GMASH_TEST_SUBREPO_BARE" ]; then
        echo "Metadata file URL line '$url_line' does not match expected 'url=$GMASH_TEST_SUBREPO_BARE'."
        return 1
    fi

    # Branch line check.
    local branch_line
    branch_line=$(grep "^branch=" "$metadata_file")
    if [ "$branch_line" != "branch=main" ]; then
        echo "Metadata file branch line '$branch_line' does not match expected 'branch=main'."
        return 1
    fi

    # Prefix line check.
    local prefix_line
    prefix_line=$(grep "^prefix=" "$metadata_file")
    if [ "$prefix_line" != "prefix=$GMASH_TEST_MONO_SUBREPO_PREFIX" ]; then
        echo "Metadata file prefix line '$prefix_line' does not match expected 'prefix=$GMASH_TEST_MONO_SUBREPO_PREFIX'."
        return 1
    fi


    # Leave monorepo dir.
    cd .. >/dev/null || return 1

    echo "$GMASH_UNIT_TEST_SEPARATOR"
    echo "[PASSED] gmash_mono_sub"
    echo "$GMASH_UNIT_TEST_SEPARATOR"
}

ut_gmash_mono_push(){
    echo "$GMASH_UNIT_TEST_SEPARATOR"
    echo "[UNIT TEST] gmash_mono_push"
    echo "$GMASH_UNIT_TEST_SEPARATOR"

    # Change into monorepo dir.
    cd "$GMASH_TEST_MONOREPO_DIR" || return 1

    # Make a change in the monorepo's subtree directory
    echo "Feature from Monorepo" >> "$GMASH_TEST_MONO_SUBREPO_PREFIX/data.txt"
    git -C "$GMASH_TEST_MONOREPO_DIR" add .
    git -C "$GMASH_TEST_MONOREPO_DIR" commit -m "feat: adding changes from monorepo"

    # Run gmash mono push command.
    "$GMASH_BINARY_PATH" mono push \
        -p "$GMASH_TEST_MONO_SUBREPO_PREFIX" \
        -r "$GMASH_TEST_MONO_SUBREPO_REMOTE" \
        -l "$GMASH_TEST_SUBREPO_BARE" \
        -b "main" \
        -B "main" > /dev/null 2>&1

    # Return code must be 0.
    local result_=$?
    if [ $result_ -ne 0 ]; then
        echo "gmash mono push command failed with exit code $result_"
        return 1
    fi

    # Verify that the changes were pushed to the subrepo.
    local subrepo_log
    subrepo_log=$(git -C "$GMASH_TEST_SUBREPO_BARE" log --oneline)
    if ! echo "$subrepo_log" | grep -q "feat: adding changes from monorepo"; then
        echo "Changes were not pushed to the subrepo."
        return 1
    fi

    # Pull changes from the subrepo remote into local to verify content.
    git -C "$GMASH_TEST_SUBREPO_DIR" pull "$GMASH_TEST_SUBREPO_BARE" main > /dev/null 2>&1

    # Verify file content in the subrepo.
    local subrepo_file_content
    subrepo_file_content=$(cat "$GMASH_TEST_SUBREPO_DIR/data.txt")
    if ! echo "$subrepo_file_content" | grep -q "Feature from Monorepo"; then
        echo "File content in the subrepo does not match expected changes."
        return 1
    fi

    # Leave monorepo dir.
    cd .. >/dev/null || return 1

    echo "$GMASH_UNIT_TEST_SEPARATOR"
    echo "[PASSED] gmash_mono_push"
    echo "$GMASH_UNIT_TEST_SEPARATOR"
}

ut_gmash_mono_push_all_single(){
    echo "$GMASH_UNIT_TEST_SEPARATOR"
    echo "[UNIT TEST] gmash_mono_push_all_single"
    echo "$GMASH_UNIT_TEST_SEPARATOR"

    # Change into monorepo dir.
    cd "$GMASH_TEST_MONOREPO_DIR" || return 1

    # Make a change in the monorepo's subtree directory
    echo "Feature from Monorepo push all" >> "$GMASH_TEST_MONO_SUBREPO_PREFIX/data.txt"
    git -C "$GMASH_TEST_MONOREPO_DIR" add .
    git -C "$GMASH_TEST_MONOREPO_DIR" commit -m "gmash mono push all single: adding changes from monorepo"

    # Run gmash mono push command.
    "$GMASH_BINARY_PATH" mono push --all > /dev/null 2>&1

    # Return code must be 0.
    local result_=$?
    if [ $result_ -ne 0 ]; then
        echo "gmash mono push command failed with exit code $result_"
        return 1
    fi

    # Verify that the changes were pushed to the subrepo.
    local subrepo_log
    subrepo_log=$(git -C "$GMASH_TEST_SUBREPO_BARE" log --oneline)
    if ! echo "$subrepo_log" | grep -q "gmash mono push all single: adding changes from monorepo"; then
        echo "Changes were not pushed to the subrepo."
        return 1
    fi

    # Pull changes from the subrepo remote into local to verify content.
    git -C "$GMASH_TEST_SUBREPO_DIR" pull "$GMASH_TEST_SUBREPO_BARE" main > /dev/null 2>&1

    # Verify file content in the subrepo.
    local subrepo_file_content
    subrepo_file_content=$(cat "$GMASH_TEST_SUBREPO_DIR/data.txt")
    if ! echo "$subrepo_file_content" | grep -q "Feature from Monorepo push all"; then
        echo "File content in the subrepo does not match expected changes."
        return 1
    fi

    # Leave monorepo dir.
    cd .. >/dev/null || return 1

    echo "$GMASH_UNIT_TEST_SEPARATOR"
    echo "[PASSED] gmash_mono_push_all_single"
    echo "$GMASH_UNIT_TEST_SEPARATOR"
}

# Config tests.
configure_testbed

# Setup test group ut_gmash_mono_1
configure_test_repo_with_local_remote "$GMASH_TEST_MONOREPO_DIR" "$GMASH_TEST_MONOREPO_BARE"
configure_test_repo_with_local_remote "$GMASH_TEST_SUBREPO_DIR" "$GMASH_TEST_SUBREPO_BARE"

# Run test group ut_gmash_mono_1
ut_gmash_mono_sub
ut_gmash_mono_push
ut_gmash_mono_push_all_single

# Open for debugging if necessary...
# explorer.exe "$(cygpath -w "$GMASH_TEST_TEMPDIR")"
