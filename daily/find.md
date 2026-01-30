---
title: find
description: finding things
published: true
date: 2026-01-30T09:07:31.816Z
tags: cmd, find, helpers
editor: markdown
dateCreated: 2026-01-30T08:35:14.914Z
---

# find
* Find suid bits
```bash
 find / -xdev -perm -4000 -exec ls -l {} \;
```

* Find world writeable files
```bash
find / -xdev -perm -o+w -and -not \( -type l -or -type s -or -perm -o+t \) -exec ls -ld {} \;
```

*Find Duplicate Files (based on size first, then MD5 hash)
```bash
find -not -empty -type f -printf "%s\n" | sort -rn | uniq -d | xargs -I{} -n1 find -type f -size {}c -print0 | xargs -0 md5sum | sort | uniq -w32 --all-repeated=separate
```

* remove files older than 60 days
```bash
find /var/log/ -type f -name '*.log' -ctime +60 -exec rm -f {} \;
```

* show what have been modified last 60 minutes
```bash
find / -mmin +60 -type f
```

* find files with lines longer than
```bash
find . -type f -exec grep -l '.\{80\}' {} \;
```

* find core dumps
```bash
/bin/nice -19  /usr/bin/find / -type f -print 2>/dev/null | egrep  -r '/core\.[0-9]{2,}' | /usr/bin/xargs ls -l
```

* count processes per user
```bash
ps hax -o user | sort | uniq -c
```

* Get the 10 biggest files/folders for the current direcotry
```bash
du -sm * .[^\.]* | sort -n | tail
```
