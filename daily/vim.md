---
title: vim
description: vim hints
published: true
date: 2026-01-31T10:39:28.545Z
tags: cmd, helpers, vim
editor: markdown
dateCreated: 2026-01-30T08:47:48.221Z
---

## Save a file you edited in vim without the needed permissions
```bash
:w !sudo tee %
```
## encrypt files
  The safest way to do this is to add the following to your ~/.vimrc file:
```bash
set cm=blowfish2
set viminfo=
set nobackup
set nowritebackup
```
Now you can crypt file with <tt> vim -x filename </tt>

## show whitespaces
```bash
:set listchars=eol:¬,tab:>·,trail:~,extends:>,precedes:<,space:␣
:set list
```

## Ansible config
The safest way to do this is to add the following to your ~/.vimrc file:
```bash
syntax on
set cursorline
set cursorcolumn
highlight CursorColumn ctermfg=White ctermbg=DarkGrey cterm=bold guifg=white guibg=yellow gui=bold
set title
set expandtab
set tabstop=2
set shiftwidth=2
set softtabstop=2
autocmd fileType yaml setlocal ai
```