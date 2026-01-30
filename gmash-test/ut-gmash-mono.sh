#!/bin/bash

# CONFIGURATION
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GMASH_BIN="$SCRIPT_DIR/../gmash"
TEST_DIR="$(mktemp -u -d "$SCRIPT_DIR/ut-mono-XXXX")"

# REPO PREPARATION
echo ">>> Preparing Test Repositories..."
SUB_REPO_PATH="$TEST_DIR/origin_sub"
MONO_REPO_PATH="$TEST_DIR/monorepo"

# MONO REMOTE SETUP
MONO_REMOTE_PATH="$TEST_DIR/mono_remote.git"
git init --bare "$MONO_REMOTE_PATH"

# Setup Subrepo
mkdir -p "$SUB_REPO_PATH"
git -C "$SUB_REPO_PATH" init -b main
git -C "$SUB_REPO_PATH" config user.email "test@test.com"
git -C "$SUB_REPO_PATH" config user.name "Tester"
echo "Subproject data" > "$SUB_REPO_PATH/sub_data.txt"
git -C "$SUB_REPO_PATH" add . && git -C "$SUB_REPO_PATH" commit -m "Initial sub"
git -C "$SUB_REPO_PATH" config receive.denyCurrentBranch ignore

# Setup Monorepo
mkdir -p "$MONO_REPO_PATH"
git -C "$MONO_REPO_PATH" init -b main
git -C "$MONO_REPO_PATH" config user.email "test@test.com"
git -C "$MONO_REPO_PATH" config user.name "Tester"
git -C "$MONO_REPO_PATH" remote add origin "$TEST_DIR/mono_remote.git"
git -C "$MONO_REPO_PATH" push -u origin main
touch "$MONO_REPO_PATH/.gitignore"
git -C "$MONO_REPO_PATH" add . && git -C "$MONO_REPO_PATH" commit -m "Initial mono"

# TEST CASE 1: SUCCESSFUL ADD
echo -e "\n\033[34m[TEST 1] Testing successful subtree add...\033[0m"
cd "$MONO_REPO_PATH"

# Run with -x for full visibility
"$GMASH_BIN" -V mono sub -p "libs/sub_project" -r "origin_sub" -l "$SUB_REPO_PATH" -b "main"
RESULT=$?

if [ $RESULT -eq 0 ] && [ -f "libs/sub_project/sub_data.txt" ] && [ -f ".gmash/subtree/origin_sub.conf" ]; then
    echo -e "\033[32mPASS: Subtree added successfully.\033[0m"
else
    echo -e "\033[31mFAIL: Subtree add failed with status $RESULT\033[0m"
    exit 1
fi

# TEST CASE 3: SUCCESSFUL PUSH
echo -e "\n\033[34m[TEST 3] Testing gmash mono push...\033[0m"

# 1. Ensure we are in the monorepo and it's clean (from previous tests)
# If you are still in a conflicted state from TEST 2, we need to abort or reset
git merge --abort 2>/dev/null || true
git reset --hard HEAD

# 2. Make a change in the monorepo's subtree directory
echo "Feature from Monorepo" >> "libs/sub_project/sub_data.txt"
git add .
git commit -m "feat: adding changes from monorepo"

# 3. Push the changes back to the sub-repository
# Using -l to point back to our local "origin_sub" folder
echo ">>> Executing mono push..."
"$GMASH_BIN" -V mono push \
    -p "libs/sub_project" \
    -r "origin_sub" \
    -l "$SUB_REPO_PATH" \
    -b "main" \
    -B "main"

RESULT=$?

# Force the subrepo to update its files to match the push that just arrived
git -C "$SUB_REPO_PATH" reset --hard HEAD

# 4. Verification: Check the standalone subrepo for the change
if [ $RESULT -eq 0 ] && grep -q "Feature from Monorepo" "$SUB_REPO_PATH/sub_data.txt"; then
    echo -e "\033[32mPASS: Changes pushed successfully to subrepo.\033[0m"
else
    echo -e "\033[31mFAIL: Push failed or changes not found in subrepo.\033[0m"
    # Show what's actually in the subrepo file for debugging
    echo "Subrepo content:"
    cat "$SUB_REPO_PATH/sub_data.txt"
    exit 1
fi

rm -rf "$TEST_DIR"