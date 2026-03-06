---
title: Git Notes
description: Helpful git comands
published: true
date: 2026-03-06T06:07:05.638Z
tags: helpers, git
editor: markdown
dateCreated: 2026-03-06T06:05:42.914Z
---

# Git Daily Commands Cheat Sheet

A practical reference for the most common Git commands used in daily development workflows.

---

# Repository Setup

## Initialize a new repository
```bash
git init
```

## Clone an existing repository
```bash
git clone <repository-url>
```

---

# Repository Status & Inspection

## Show repository status
```bash
git status
```

## Show commit history
```bash
git log
```

## Compact commit history
```bash
git log --oneline --graph --decorate
```

## Show changes not yet staged
```bash
git diff
```

## Show staged changes
```bash
git diff --staged
```

---

# Adding and Committing Changes

## Add a single file
```bash
git add file.txt
```

## Add all changes
```bash
git add .
```

## Create a commit
```bash
git commit -m "commit message"
```

## Commit all modified tracked files
```bash
git commit -am "commit message"
```

---

# Remote Repositories

## Show configured remotes
```bash
git remote -v
```

## Add a remote repository
```bash
git remote add origin <repository-url>
```

## Fetch changes from remote
```bash
git fetch
```

## Pull latest changes
```bash
git pull
```

## Push local commits
```bash
git push
```

---

# Branch Management

## List branches
```bash
git branch
```

## Create a new branch
```bash
git branch feature-x
```

## Switch to a branch
```bash
git switch feature-x
```

## Create and switch branch
```bash
git switch -c feature-x
```

## Delete a branch
```bash
git branch -d feature-x
```

---

# Merging

## Merge another branch into current branch
```bash
git merge feature-x
```

## Abort merge
```bash
git merge --abort
```

---

# Undo and Restore Changes

## Restore a file to last commit
```bash
git restore file.txt
```

## Restore all files
```bash
git restore .
```

## Remove file from staging area
```bash
git restore --staged file.txt
```

## Amend the last commit
```bash
git commit --amend
```

## Reset last commit but keep changes
```bash
git reset --soft HEAD~1
```

## Hard reset to last commit
```bash
git reset --hard HEAD
```

---

# Working with Stash

## Save current changes temporarily
```bash
git stash
```

## List stashes
```bash
git stash list
```

## Restore latest stash
```bash
git stash pop
```

---

# File Operations

## Remove a file from repository
```bash
git rm file.txt
```

## Rename or move a file
```bash
git mv oldname.txt newname.txt
```

---

# Apply Updated .gitignore Rules

If you updated `.gitignore` but files are already tracked:

```bash
git rm -r --cached .
git add .
git commit -m "Remove ignored files"
```

---

# Useful Debugging Commands

## Show commits where a file was deleted
```bash
git log --diff-filter=D --summary
```

## Restore a file from a specific commit
```bash
git checkout <commit-hash> -- path/to/file
```

---

# Useful Aliases

```bash
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --decorate"
git config --global alias.co checkout
```

Example usage:

```bash
git st
git lg
```

---

# Typical Daily Workflow

```bash
git pull
git status
git add .
git commit -m "update feature"
git push
```

---

# Quick Tip

If something looks wrong, run:

```bash
git status
```

This command usually tells you exactly what Git expects next.