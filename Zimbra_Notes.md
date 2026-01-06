---
title: Zimbra Notes
description: My Personal Notes about Zimbra
published: true
date: 2026-01-06T17:37:57.798Z
tags: personal, referencecards, zimbra
editor: markdown
dateCreated: 2026-01-06T05:27:07.210Z
---


# Configuration
## Restrict Zimbra Senders to Distribution List
Recently I had some spam on internal distribution lists.
That was too bad, because it was a first class credit card fake :-)
So I searched and found a simple way to only allow domain sender address to send email to distribution lists.
That solved my problem.

Here is how I did it
```bash
zmprov modifyConfig zimbraMilterServerEnabled TRUE
zmmilterctl restart
zmmilterctl status

ZDOMAIN=mydomain.ch
zmprov gadl $ZDOMAIN | while read dl_email
do
   echo "---- deny all senders to $dl_email"
   zmprov grr dl $dl_email pub -sendToDistList
   echo "---- allow $ZDOMAIN senders to $dl_email"
   zmprov grr dl $dl_email dom $ZDOMAIN sendToDistList
done

zmmtactl reload
```
This is a good site to read more details:
* https://wiki.zimbra.com/wiki/Enabling_and_administering_the_Zimbra_milter

## Change Galsync Account
```bash
zmprov modifyDomain mydomain.ch zimbraGalAccountId 42ef46f3-bc1e-4795-8fca-42d8c3c597bd

zmprov gd mybuehl.ch | egrep -i 'ldap|gal'
   zimbraGalAccountId: 42ef46f3-bc1e-4795-8fca-42d8c3c597bd

#login to zimbra admin and tick "hide in GAL" on galsync account

zmgsautil createAccount -a galsync@mydomain.ch -n InternalGAL --domain mydomain.ch -t zimbra -f _InternalGAL
   galsync@mydomain.ch    42ef46f3-bc1e-4795-8fca-42d8c3c597bd

zmgsautil forceSync -a galsync@mydomain.ch -n InternalGAL

# login to old galsync account (admin) and remove _InternalGAL folder from address book
```

## get signatures of all users
* get all signatures
```bash
#!/bin/bash

DIR=/opt/scripts/sig

id | grep zimbra || (echo "ERROR: start it as user zimbra" ; pkill -9 $$)

clear
mkdir -p $DIR
echo "Retrieve zimbra user name..."

USERS=`zmprov  sa  -v zimbraMailDeliveryAddress="*@stiftung-buehl.ch" | grep zimbraMailAlias | sed 's/.*: //' | grep -e '^b....@' -e '^e....@' | cut -d'@' -f1 | sort -u`

for ACCOUNT in $USERS
do
  NAME=`echo $ACCOUNT`
  zmprov getSignatures $NAME > $DIR/$NAME.txt
  echo "Export signature for $NAME..."
done
echo "All signature has been export successfully"
</pre>
* split all signatures
<pre>
#!/bin/bash

DIR=/opt/scripts/sig

id | grep zimbra || (echo "ERROR: start it as user zimbra" ; pkill -9 $$)

mkdir -p $DIR

cd $DIR

ls -1 *.txt | while read f
do
  echo "   ---   $f   ---"
  cat "$f" | while read line
  do
    if (echo "$line" | grep -q "^# name ") ; then true
    elif (echo "$line" | grep -q "^zimbraSignatureId: ") ; then true
    elif (echo "$line" | grep -q "^$") ; then true
    elif (echo "$line" | grep -q "^zimbraPrefMailSignatureHTML:")
    then
      echo "$line" | sed 's/zimbraPrefMailSignatureHTML://' > tmp.sig
    elif (echo "$line" | grep -q "^zimbraSignatureName: ")
    then
      sed -i '/^$/d' tmp.sig
      mv tmp.sig "$(echo $line | sed 's/zimbraSignatureName: //' )_$f.txt"
      echo tmp.sig "$(echo $line | sed 's/zimbraSignatureName: //' )_$f.txt"
    else
      echo "$line" >> tmp.sig
    fi
  done
  mv "$f" "$f.done"
done
```

## Zimbra Backup
* show backup config
`zmschedulebackup -q`
`zmschedulebackup -s`
`crontab -l | grep backup`

* set backup config
`zmschedulebackup -R --mail-report d 1m "0 0 * * *" --mail-report i "0 1 * * 0-5" -a all --mail-report f "0 1 * * 6"`
`crontab -l | grep backup`

## Change Webmail Font for all Users
`zmprov mc default zimbraPrefHtmlEditorDefaultFontFamily "Sans Serif"`

## Change Password Changing URL
`zmprov md mydomain.ch zimbraChangePasswordURL https://password.mydomain.ch`

# Zimbra debugging
## Check all users Trash folders for mails older than 40 days
```bash
USERS=`zmprov -l gaa | sort`
for ACCOUNT in $USERS
do
  echo "------- $ACCOUNT -------"
  zmmailbox -z -m $ACCOUNT s -l50 -t message "in:trash before:$(date -d '-40 day' +%m/%d/%y)"
done
```

## Zimbra debugging in web browser
* http://zimbra.domain.com/zimbra/?dev=1

## Zimbra debugging to logfile
`zmprov aal <username> zimbra.soap debug #mailbox.log` 
`zmprov ral <username> # stop logging`

## comandline calendar queries
`zmmailbox -z -m <username> gf Calendar`
`zmmailbox -z -m <username> gaps -5day +5day  /Calendar`
`zmmailbox -z -m <username> search -t appointment in:Calendar`

## comandline adressbook queries
`zmmailbox -z -m <username> gact -f '/Öffentliche Adressbücher/Verteilerlisten'`

## list all accounts
`zmprov  -m -l gaa`

## zimbra user query in mysql db
```bash
su - zimbra
mysql
use zimbra
select * from mailbox where account_id = "<USER-UUID>"\G
```

## restore mailbox with prefix in username
`zmrestore -a user@domain.com -ca -pre temp_`

## find username from USER-UUID
`zmprov getAccount <USER-UUID> mail`

## get zimbraID of account
`zmprov ga <username> zimbraId`