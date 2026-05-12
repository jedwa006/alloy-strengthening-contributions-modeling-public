#!/usr/bin/env bash
# Filter the current checkout into a clean tree suitable for the public mirror,
# then push it to the public-mirror remote. Designed to be idempotent and
# callable both from CI (.github/workflows/sync-public-mirror.yml) and from
# a developer machine for testing.
#
# Strategy: full history rewrite via git-filter-repo, removing files that are
# private (literature PDFs we don't have rights to redistribute), then a
# `--force` push to the public mirror. Each run produces a single coherent
# history snapshot of the current state.
#
# Required environment:
#   PUBLIC_REMOTE_URL    https URL of the public mirror repo, including a
#                        token if needed for auth (CI sets this; locally you
#                        can use SSH form: git@github.com:user/repo-public.git)
#   PUBLIC_REMOTE_BRANCH branch to push to (default: main)
set -euo pipefail

PUBLIC_REMOTE_BRANCH="${PUBLIC_REMOTE_BRANCH:-main}"
WORK_DIR="${WORK_DIR:-/tmp/public-mirror-$$}"

if [[ -z "${PUBLIC_REMOTE_URL:-}" ]]; then
    echo "ERROR: PUBLIC_REMOTE_URL must be set" >&2
    exit 1
fi

if ! command -v git-filter-repo >/dev/null 2>&1; then
    echo "ERROR: git-filter-repo not installed. Try: pip install git-filter-repo" >&2
    exit 1
fi

# Operate on a fresh clone in /tmp so we don't touch the developer's working repo.
echo "==> Cloning current repo into $WORK_DIR"
rm -rf "$WORK_DIR"
git clone --no-local "$(git rev-parse --show-toplevel)" "$WORK_DIR"
cd "$WORK_DIR"

# Drop the original origin so filter-repo's safety check is satisfied.
git remote remove origin || true

# Files / regexes that must NOT appear in the public mirror.
# Add new patterns here when you have more private content. Using regex
# rather than glob because git-filter-repo's --path-glob uses fnmatch where
# '**' doesn't cross directory separators reliably; regex catches everything
# below the named directory at any depth.
#
# Why .github/workflows/ is excluded: the sync workflow is a tool of the
# private repo, not project content. Including it in the public mirror would
# require giving the sync PAT the `workflow` scope, which is broader than
# needed (the PAT only ever needs to write to the mirror's contents).
#
# Why data/xrd/experimental/ is excluded: raw XRD spectra are large source
# files specific to the user's experimental work; the public mirror should
# only carry derived analyses + plots, not the source data files.
#
# Why "reference docs/Chapter [N]_Refs_*" is excluded ENTIRELY (including
# .bib files): these folders accompany pre-publication draft chapters. The
# folder + bib together fingerprint exactly which papers an unsubmitted
# manuscript is citing — that's scoping leakage we'd rather avoid until
# the chapter is submitted/published. Once submission is public, the
# folder can be moved out from under this exclusion if desired.
echo "==> Rewriting history to remove private content"
git filter-repo --force \
    --path-regex '^pdf-archive/.*\.pdf$' \
    --path-regex '^reference docs/.*\.pdf$' \
    --path-regex '^reference docs/Chapter [0-9]+_Refs_.*$' \
    --path-regex '^\.github/workflows/.*\.ya?ml$' \
    --path-regex '^data/xrd/experimental/.*$' \
    --path-regex '^data/nanoindentation/experimental/.*$' \
    --path-regex '^data/tensile/experimental/.*$' \
    --invert-paths

# Verify the filter worked: no PDFs in any commit.
echo "==> Verifying no PDFs survived the filter"
SURVIVED="$(git log --all --pretty=format: --name-only --diff-filter=A | grep -E '\.pdf$' || true)"
if [[ -n "$SURVIVED" ]]; then
    echo "ERROR: PDFs survived the history filter:" >&2
    echo "$SURVIVED" >&2
    exit 1
fi
echo "    OK — no PDFs in rewritten history"

# Push to the public mirror.
echo "==> Pushing to public mirror at $PUBLIC_REMOTE_URL (branch $PUBLIC_REMOTE_BRANCH)"
git remote add public "$PUBLIC_REMOTE_URL"
git push public "HEAD:$PUBLIC_REMOTE_BRANCH" --force

echo "==> Done. Cleaning up $WORK_DIR"
cd /
rm -rf "$WORK_DIR"
