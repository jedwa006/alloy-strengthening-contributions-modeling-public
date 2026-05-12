# Public Mirror Setup

This repo stays **private** because it tracks copyrighted literature PDFs we
don't have rights to redistribute. To share progress with collaborators
(e.g. an advisor) without forcing them to create a GitHub account or
requiring you to invite them as a collaborator, the model code, docs,
notebooks, and indexes are auto-mirrored to a **public sibling repo**.

The mirror is rebuilt on every push to `main` of the private repo, with the
literature PDFs filtered out of history via `git-filter-repo`. The public
mirror is **a one-way reflection** — never edit it directly; it gets
force-overwritten on each sync.

## What ends up in the public mirror

Everything except files matching the private-content patterns in
[`scripts/build_public_mirror.sh`](../scripts/build_public_mirror.sh):

- `pdf-archive/*.pdf`             — literature PDFs we don't have rights to redistribute
- `reference docs/**/*.pdf`       — same
- `.github/workflows/**/*.yml`    — sync workflow is a private-repo tool
- `data/xrd/experimental/**/*`    — raw experimental XRD source files

Manifests, indexes, derived analyses, and code that uses the data **remain
in the public mirror** — `pdf-archive/MANIFEST.md`, `references/references.bib`,
and `data/README.md` all sync, so anyone reading the public mirror can see
what data exists and fetch the source files via Zotero / institutional
access (for PDFs) or by request (for experimental data).

## One-time setup (you do this once, then forget about it)

### 1. Create the public mirror repo

```bash
gh repo create jedwa006/alloy-strengthening-contributions-modeling-public \
    --public \
    --description "Public mirror of M54 strengthening + toughening model. Sourced from a private repo; do not commit here directly." \
    --homepage "https://github.com/jedwa006/alloy-strengthening-contributions-modeling-public"
```

(Adjust the name if you want a different one — just match it in step 3.)

### 2. Create a fine-grained Personal Access Token

GitHub → Settings → Developer settings → Personal access tokens →
Fine-grained tokens → "Generate new token".

- **Resource owner:** your account (`jedwa006`)
- **Repository access:** Only select repositories →
  `alloy-strengthening-contributions-modeling-public`
- **Repository permissions:** Contents: **Read and write**
- **Expiration:** 1 year (then renew)

Copy the token value (you'll only see it once).

### 3. Add the secret + variable to the **private** repo

Go to the private repo → Settings → Secrets and variables → Actions:

- **Secrets** tab → "New repository secret"
  - Name: `PUBLIC_MIRROR_TOKEN`
  - Value: paste the token from step 2
- **Variables** tab → "New repository variable"
  - Name: `PUBLIC_MIRROR_REPO`
  - Value: `jedwa006/alloy-strengthening-contributions-modeling-public`

### 4. Trigger the first sync

The workflow runs automatically on push to `main`. To trigger it
immediately for the first time without making a code change, go to the
private repo → Actions tab → "Sync to public mirror" → "Run workflow".

After ~1 minute, the public mirror is populated. Send your advisor:
`https://github.com/jedwa006/alloy-strengthening-contributions-modeling-public`

## Adding new private-content patterns later

If you add other content that shouldn't be public (e.g. raw experimental
data with embargo, draft manuscript files), edit the `git filter-repo`
invocation in [`scripts/build_public_mirror.sh`](../scripts/build_public_mirror.sh):

```bash
git filter-repo --force \
    --path-regex '^pdf-archive/.*\.pdf$' \
    --path-regex '^reference docs/.*\.pdf$' \
    --path-regex '^data/raw/.*\.csv$' \         # ← new pattern
    --invert-paths
```

Push the change to `main`; the next sync will retroactively scrub any new
patterns from the public-mirror history.

## Testing the filter locally

You can dry-run the filter against a temp clone of the current repo
without touching the real public mirror by setting the URL to a throwaway
local target:

```bash
# Create a local bare repo to push into (so we can inspect the result)
git init --bare /tmp/test-public-mirror.git

PUBLIC_REMOTE_URL=/tmp/test-public-mirror.git \
PUBLIC_REMOTE_BRANCH=main \
./scripts/build_public_mirror.sh

# Inspect: should have everything from your repo EXCEPT the PDFs
git clone /tmp/test-public-mirror.git /tmp/test-public-mirror-clone
ls /tmp/test-public-mirror-clone/pdf-archive/   # should show only MANIFEST.md, .gitkeep
ls /tmp/test-public-mirror-clone/reference\ docs/  # should be empty (or just subfolders)
du -sh /tmp/test-public-mirror-clone/.git/      # should be small (~5 MB) vs source's ~440 MB
```

## Troubleshooting

- **"git-filter-repo not installed"** in the Action: the workflow installs
  it via pip; if it ever stops working, check the runner image's Python
  version.
- **Push rejected to public mirror**: token expired (rotate per step 2)
  or the repository variable points at a non-existent repo.
- **PDFs leak into the public mirror**: they shouldn't (the script
  verifies this and exits non-zero if any survive). If somehow they did,
  re-run the workflow to overwrite, then audit the filter glob list.
