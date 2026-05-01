# Codeberg migration

Small helper repo for migrating public GitHub repositories to Codeberg.

## What this does

This project contains scripts used to:

- clone public GitHub repositories as local bare mirrors;
- create or prepare matching repositories on Codeberg;
- push normal branches and tags to Codeberg;
- avoid GitHub-specific pull request refs such as `refs/pull/*`, which Codeberg rejects;
- audit the migration afterwards.

The cloned repositories themselves are intentionally not tracked by this repo.

## Folder layout

```text
codeberg-migration/
├── clean_push_codeberg.py       # Push local bare mirrors to Codeberg with a progress bar
├── audit_after_migration.sh     # Audit migrated repos for common missing pieces
├── repos.tsv                    # GitHub repo inventory
├── repos_https.tsv              # GitHub repo inventory with HTTPS URLs
├── cloned-repos/                # Local bare mirrors, ignored by Git
└── push_logs/                   # Local push logs, ignored by Git
```

## Required environment variables

```bash
export CODEBERG_USER="thefrenchartist"
export CODEBERG_TOKEN="your_codeberg_token"
```

## Push all local mirrors to Codeberg

```bash
cd ~/codeberg-migration
./clean_push_codeberg.py
```

The script pushes:

```text
refs/heads/* -> refs/heads/*
refs/tags/*  -> refs/tags/*
```

It intentionally does not use:

```bash
git push --mirror
```

because GitHub mirror clones include refs like:

```text
refs/pull/1/head
refs/pull/1/merge
```

and Codeberg rejects those hidden refs.

## Audit after migration

```bash
cd ~/codeberg-migration
./audit_after_migration.sh
```

The audit checks for:

- Git LFS usage;
- submodules;
- repositories using `master` but not `main`;
- `gh-pages` branches;
- GitHub Actions workflows.

## Notes

This migrates Git history: branches and tags.

It does not automatically migrate GitHub platform metadata such as:

- issues;
- pull request discussions;
- GitHub Actions secrets;
- GitHub Pages settings;
- branch protection rules;
- releases and release assets.
