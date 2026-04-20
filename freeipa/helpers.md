---
title: helpers
description: Helpers and Knowledge for FreeIPA / IDM
published: true
date: 2026-04-20T15:47:58.945Z
tags: freeipa
editor: markdown
dateCreated: 2026-02-18T11:03:52.490Z
---

# Doumentation

## Scripts
[FreeIPA linux.scripts repo](https://github.com/search?q=repo%3Ajoe-speedboat%2Flinux.scripts+freeipa&type=code)

## sudo
### sudo rule order evaluation

> * The General area of a sudo rule
In this area, you can modify the rule's description and sudo order. The sudo order field accepts integers and defines the order in which IdM evaluates the rules. 
`The rule with the highest sudo order value is evaluated first.`
{.is-info}

### passwordless sudo
> In sudo rule option, set `!authenticate`