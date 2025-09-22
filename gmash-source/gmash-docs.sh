#!/bin/bash
#@doc---------------------------------------------------------------------------------------------#
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright(c) 2025 Anton Yashchenko
#-------------------------------------------------------------------------------------------------#
# @project: [gmash] Git Smash
# @author(s): Anton Yashchenko
# @website: https://www.acpp.dev
#-------------------------------------------------------------------------------------------------#
# @file GMash documentation generator script.
# @created: 2025/09/21
# @brief
#@enddoc------------------------------------------------------------------------------------------#

readonly GMASH_DOCS_BIN="$GMASH_SOURCE/../docs"
echo -e "\e[31;1m  ⚙  Generating gmash documentation. Path : $GMASH_DOCS_BIN \e[0m"
cd "$GMASH_DOCS_BIN" || exit 1

# dirs
echo "[helptext] gmash dirs prefix -h | helptext -o cmd-dirs-prefix.md"
gmash dirs prefix -h | helptext -o cmd-dirs-prefix.md

echo "[helptext] gmash dirs same -h | helptext -o cmd-dirs-same.md"
gmash dirs same -h | helptext -o cmd-dirs-same.md

echo "[helptext] gmash dirs separate -h | helptext -o cmd-dirs-separate.md"
gmash dirs separate -h | helptext -o cmd-dirs-separate.md

echo "[helptext] gmash dirs squash -h | helptext -o cmd-dirs-squash.md"
gmash dirs squash -h | helptext -o cmd-dirs-squash.md

# find
echo "[helptext] gmash find duplicate-code -h | helptext -o cmd-find-duplicate-code.md"
gmash find duplicate-code -h | helptext -o cmd-find-duplicate-code.md

echo "[helptext] gmash find gits -h | helptext -o cmd-find-gits.md"
gmash find gits -h | helptext -o cmd-find-gits.md

echo "[helptext] gmash find sources -h | helptext -o cmd-find-sources.md"
gmash find sources -h | helptext -o cmd-find-sources.md

# gist
echo "[helptext] gmash gist clone -h | helptext -o cmd-gist-clone.md"
gmash gist clone -h | helptext -o cmd-gist-clone.md

echo "[helptext] gmash gist create -h | helptext -o cmd-gist-create.md"
gmash gist create -h | helptext -o cmd-gist-create.md

echo "[helptext] gmash gist delete -h | helptext -o cmd-gist-delete.md"
gmash gist prepare -h | helptext -o cmd-gist-prepare.md

echo "[helptext] gmash gist prepare -h | helptext -o cmd-gist-prepare.md"
gmash gist recover -h | helptext -o cmd-gist-recover.md

echo "[helptext] gmash gist recover -h | helptext -o cmd-gist-recover.md"
gmash gist upload -h | helptext -o cmd-gist-upload.md

# lineage
echo "[helptext] gmash lineage merge -h | helptext -o cmd-lineage-merge.md"
gmash lineage merge -h | helptext -o cmd-lineage-merge.md

# subtree
echo "[helptext] gmash subtree new -h | helptext -o cmd-subtree-new.md"
gmash subtree new -h | helptext -o cmd-subtree-new.md

echo "[helptext] gmash subtree pull -h | helptext -o cmd-subtree-pull.md"
gmash subtree patch -h | helptext -o cmd-subtree-patch.md

# mono
echo "[helptext] gmash mono patch -h | helptext -o cmd-mono-patch.md"
gmash mono patch -h | helptext -o cmd-mono-patch.md

echo "Documentation generation complete."