---
title: Inbox
description: NanoBob's Notekeeping page
published: true
date: 2026-03-06T14:48:35.678Z
tags: 
editor: markdown
dateCreated: 2026-03-06T13:20:36.385Z
---

# NanoBob's Notes

### 2026-03-06 15:18

hi bob asdfasdf
this is great, i love you... Fri Mar  6 03:18:26 PM CET 2026

### 2026-03-06 15:48

_knd_complete() {
    local curr_arg=""
    COMPREPLY=( $(kubectl get namespaces --no-headers -o custom-columns=":metadata.name" | grep "^$curr_arg") )
}

knd() {
    if [[ -n "$1" ]]; then
        kubectl config set-context --current --namespace="$1"
    else
        echo "Usage: knd <namespace>"
        echo "Available namespaces:"
        kubectl get namespaces --no-headers -o custom-columns=":metadata.name"
    fi
}

complete -F _knd_complete knd