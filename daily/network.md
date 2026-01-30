---
title: network
description: network related
published: true
date: 2026-01-30T16:07:33.674Z
tags: cmd, helpers, networking
editor: markdown
dateCreated: 2026-01-30T15:19:30.476Z
---

## Proxy environment variables
* https://about.gitlab.com/blog/2021/01/27/we-need-to-talk-no-proxy/
* `$HOME/.bashrc`
```bash
export http_proxy=http://proxy.example.com:8080
export no_proxy=whole-domain-direct.com,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```
`/etc/environment`
```bash
http_proxy=http://proxy.example.com:8080
no_proxy=whole-domain-direct.com,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```
|                       | curl      | wget           | Ruby      | Python    | Go        |
| --------------------- | --------- | -------------- | --------- | --------- | --------- |
| no_proxy              | Yes       | Yes            | Yes       | Yes       | Yes       |
| NO_PROXY              | Yes       | No             | Yes       | Yes       | Yes       |
| Case precedence       | lowercase | lowercase only | lowercase | lowercase | Uppercase |
| Matches suffixes?     | Yes       | Yes            | Yes       | Yes       | Yes       |
| Strips leading .?     | Yes       | No             | Yes       | Yes       | No        |
| * matches all hosts?  | Yes       | No             | No        | Yes       | Yes       |
| Supports regexes?     | No        | No             | No        | No        | No        |
| Supports CIDR blocks? | No        | No             | Yes       | No        | Yes       |
| Detects loopback IPs? | No        | No             | No        | No        | Yes       |

## blink NIC LED for 5 minutes
```bash
NIC=$(ip route show default 0.0.0.0/0 | awk '{print $5; exit}')
END=$((SECONDS+300))
while [ $SECONDS -lt $END ]; do
    ip link set $NIC down
    sleep 2
    ip link set $NIC up
    sleep 2
done
```

## change description of ssh private key
* change comment of private key
  https://stackoverflow.com/questions/73676798/rename-ssh-key-agent-that-was-already-added
```bash
ssh-keygen -c -C 'migration:rundeck@host' -f ssh/id_rsa_migration
  Enter passphrase:
  Old comment: rundeck@host
  Comment 'migration:rundeck@host' applied
```
* verify added keys
```bash
ssh-add -l
```

## private key handling with keychain in `$HOME/.bashrc`
```bash
# SSH
keychain -Q -q ~/.ssh/id_dsa < /dev/null
[ -f $HOME/.keychain/$HOSTNAME-sh ] && source $HOME/.keychain/$HOSTNAME-sh

#GPG Keys
#gpg --list-keys
keychain --agents gpg 297E196D
[ -f $HOME/.keychain/$(uname -n)-sh-gpg ] && source $HOME/.keychain/$(uname -n)-sh-gpg
```

## use keychain to protect your Ansible SSH private Keys
* on control node, install keychain
```bash
dnf -y install keychain
```

* on control node, with the ansible user do add keychain
`vi .bashrc`
```
keychain -Q -q ~/.ssh/id_rsa < /dev/null
[ -f $HOME/.keychain/$HOSTNAME-sh ] && source $HOME/.keychain/$HOSTNAME-sh
```

* protect your ssh key
```bash
[ansible-adm@control-node ~]$ ssh-keygen -p -f .ssh/id_rsa
  Key has comment '.ssh/id_rsa'
  Enter new passphrase (empty for no passphrase): 
  Enter same passphrase again: 
  Your identification has been saved with the new passphrase.
```

* log out and log in, it will ask for pass phrase
```bash
[ansible-adm@control-node ~]$ exit
  Connection to control-node closed.
  [user@jump ~]$ ansible-adm@control-node 
  Last login: Thu Sep 29 11:39:00 2016 from 17.2.25.25
  Enter passphrase for /home/ansible-adm/.ssh/id_rsa: 
```
* now you can add cronjobs that run ansible commands
  remember you have to login once after every reboot of control-node
```bash
crontab -e
  SHELL="/bin/bash"
  PATH=/usr/local/bin:/bin:/usr/bin:$HOME/bin
  * * * * * . $HOME/.bashrc; cd dep-adhoc ; ansible all -m ping >> cron.out 2>&1
```
* check results
```bash
cat cron.out 

server1.example.com | SUCCESS => {
    "changed": false, 
    "ping": "pong"
}
localhost | SUCCESS => {
    "changed": false, 
    "ping": "pong"
}
```

## generate random MAC address
```bash
printf 'DE:AD:BE:EF:%02X:%02X\n' $((RANDOM%256)) $((RANDOM%256))
date +%s |md5sum|sed 's/^\(..\)\(..\)\(..\)\(..\)\(..\).*$/02:\1:\2:\3:\4:\5/'
```

## Serve current directory tree at by http port 8000 on local machine
python3 -m http.server
python2 -m SimpleHTTPServer

## find routing decision
ip route show match 1.2.3.4
ip route get 1.2.3.4

## set ip address on the fly
ip link set eth0 up
ip addr add 192.168.111.1/24 dev eth0
ip route add 192.168.33.1/32 dev eth0
ip route add default via 192.168.0.254 dev eth0

## pipe tar via ssh
* put data
cd /usr/local/stuff
tar cfz - . | ssh remote "cd /backup && tar xfz -"

* get data
ssh remote "cd /usr/local/stuff && tar cf - ." | tar xfz -

## pipe disc image via ssh
* get data
ssh  root@get-disk-from dd bs=8192 if=/dev/sda | dd bs=8192 of=/dev/vg01/backup_sda

* put data
dd bs=8192 if=/dev/sda | ssh  root@put-disc-to dd bs=8192 of=/dev/vg01/backup_sda
dd if=/dev/sda1 | buffer -s 64k -S 10m | ssh root@put-disk-to "cat > /dev/image"
dd if=/dev/sda1 bs=4M | lzop -c | ssh root@put-disk-to "lzop -dc | dd of=/dev/sda1 bs=4M"

## escape remote console
* by telnet / Xen VM Console
```
Escape character is '^]'.<br>
```
and that means: `<CTRL> + <AltGr> + ]`

* access ilo by ssh
```
ssh user@ilo-host
</>hpiLO-> remcons
Starting remote console
Press 'ESC (' to return to the CLI Session
```

* from cyclades
`~.`

## install public key on remote machine

ssh-copy-id username@hostname

## Resume rsync of a big file
rsync --partial --progress --rsh=ssh  $file_source $user@$host:$destination_file

## install ssh pub keys from users github account
curl -s https://github.com/joe-speedboat.keys | while read key ; do 
   grep -q "$key" ~/.ssh/authorized_keys && echo "Key did exist: $key"|| (echo "$key" >> ~/.ssh/authorized_keys ; echo "Key added: $key" )
done


## ssh port forwarding
* ssh reverse tunnel
 #build the ssh reverse tunnel
 user@destination$ ssh -R 2222:localhost:22 middleuser@middle
 user@destination$ ssh -N -f -R 2222:localhost:22 middleuser@middle
 #connect to the ssh reverse tunnel and jump to destination
 middleuser@middle$ ssh destinationuser@localhost -p2222
 user@notebook$ ssh destinationuser@middle -p 2222


* ssh port forwarding
 ssh -g -L 80:127.0.0.1:3128 jump@zen.bitbull.ch -p23
 ssh -g -L local_port:remote_host:remote_port  user@dst_host -p23
   -g  >  Allows remote hosts to connect to local forwarded ports
   -L  >  [bind_address:]port:host:hostport
   -p  >  use different port for ssh connection
   
## remember ssh private key passphrase on console
alias skey='ssh-agent > /tmp/.k ; . /tmp/.k ; rm -f /tmp/.k ; ssh-add'



==remember ssh private key passphrase in gnome session==
 # install rpm
 yum -y install openssh-askpass
 # now add asking dialog to gnome user
 # Gnome Menu > System > Preferences > More Preferences > Sessions > Tab:Startub Programs > Add
 # after restart of gnome: Gnome Menu > System > Preferences > More Preferences > Sessions > Tab:Current Session (ssh-add) -> set order to 90
 # type in: /usr/bin/ssh-add

==validate date of ssl certificate==
 echo | openssl s_client -connect www.google.com:443 2>/dev/null |openssl x509 -dates -noout

<pre>
ssl-test() { curl -kvv --max-time 2 https://$1 2>&1 | egrep 'issuer:|expire date:|start date:|subject:' ;}

ssl-test www.google.ch
   *  subject: C=US; ST=California; L=Mountain View; O=Google LLC; CN=*.google.ch
   *  start date: Jan  5 12:14:12 2021 GMT
   *  expire date: Mar 30 12:14:11 2021 GMT
   *  issuer: C=US; O=Google Trust Services; CN=GTS CA 1O1
</pre>

==add cacert to java keystore==
<pre>
TMPF=/tmp/myca.crt
EP="directory01.sun.bitbull.ch:636"
echo -n | openssl s_client -connect $EP |    sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > $TMPF
openssl x509 -in $TMPF
keytool -import -alias idm -file $TMPF -keystore /etc/pki/ca-trust/extracted/java/cacerts -storepass changeit
</pre>

==SSL/TLS debugging==
* Get all LISTEN Ports and test for Certificate details by web request
<pre>
IF=$(ip r | grep default | awk '{print $5}')
IP=$(ip addr show $IF | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
lsof -i -P -n 2>/dev/null | grep LISTEN | grep -v 127.0.0.1 | awk '{print $9}' | cut -d: -f2 | sort -u | while read port 
do 
   echo "---------- https://$IP:$port "
   lsof -i -P -n 2>/dev/null | grep LISTEN | grep :$port 
   curl -m3 -k -vv https://$IP:$port 2>&1 | grep -A4 'Server certificate:'
done
</pre>

==tcpdump==
 # max. 100MB /  full length and host x.x.x.x   
 tcpdump -C 100 -w dump.dat -i eth0 -s 0 -XX udp port 514
 tcpdump host client.example.com and port 80
 tcpdump ip host bevo and bevo master
 tcpdump ip and not net 127.0.0.0
To print the start and end packets (the SYN and FIN packets) of each TCP conversation that involves a non-local host
 tcpdump \(tcp[13] \& 3 !=0 and not src and dst net localnet\)
To print all ICMP packets that are not echo requests or replies (not ping packets)
 tcpdump \(icmp[0] !=8 and icmp[0] !=0\)
Dump Traffic for later view in Wireshark
 tcpdump -p -s0 -w tcpdump.cap
Trace plain LDAP traffic
  tcpdump -nvvvXAttt  port 389 2>&1  | grep -B1 -A1 dc=




==conunt network connections for each host==
 netstat -an | grep ESTABLISHED | awk '{print $5}' | awk -F: '{print $1}' | sort  | uniq -c | sort

==List the number and type of active network connections==
 netstat -ant | awk '{print $NF}' | grep -v '[a-z]' | sort | uniq -c

==nmap network discovery==
* find web servers on subnet
 nmap -sS -T5 -P0 -p80 -oG - 192.168.1.1-254 | grep open

==monitor network activity of applications==
 while true 
 do 
    date
    diff  <(lsof -i) <(sleep 5; lsof -i) 
 done

==Analyse an Apache access log for the most common IP addresses==
 tail -10000 access_log | awk '{print $1}' | sort | uniq -c | sort -n | tail

==show apps that are using network connection==
 lsof -P -i -n

==show your wanip==
 curl ifconfig.me

==scan open outgoing ports==
 for i in {1..1024}; do wget -qO- -T0.5 -t1 portquiz.net:$i >/dev/null 2>&1 && echo $i open ; done




==curl webdav examples==
* Reading Files/Folders on Webdav Server
 curl 'https://example.com/webdav'
* Deleting Files/Folders on Webdav Server
 curl -X DELETE 'https://example.com/webdav/test'
:* Similarly for deleting file test.txt
 curl -X DELETE 'https://example.com/webdav/test.txt'
* Renaming File on Webdav Server
 curl -X MOVE --header 'Destination:http://example.org/new.txt' 'https://example.com/old.txt'
* Creating new foder on Webdav Server:
 curl -X MKCOL 'https://example.com/new_folder'
* Uploading File on Webdav Server
 curl -T '/path/to/local/file.txt' 'https://example.com/test/'
* CURL --Options
:* Username/Password
 curl --user 'user:pass' 'https://example.com'
:* HTTP Authentication
 curl --user 'user:pass' 'https://example.com' --basic
 curl --user 'user:pass' 'https://example.com' --digest
:* curl decide the authentication
 curl --user 'user:pass' 'https://example.com' --anyauth
:* Get Response Code
 curl --user 'user:pass' -X DELETE 'https://example.com/test' -sw '%{http_code}'

==nextcloud upload to shared link with curl==
* acess with no password -> copy uuid url:
<pre>https://cloud.domain.org/s/EaaddddcMMt2aZb</pre>
* Upload file with this curl oneliner (adjust token and url):
<pre>curl -u EaaddddcMMt2aZb: -H "X-Requested-With: XMLHttpRequest" "https://cloud.domain.org/public.php/webdav/" -T mynotes.txt</pre>
* Get friday beer, beacause your work is save now !!!
: (reuse this instruction every friday :-)

==use netcat port check==
 nc -vvn -z 10.202.3.40 80 #old syntax
 nc -w3 -i3 --recv-only $DSL_IP $DSL_PORT 2>/dev/null | grep -q Login: #new syntax

==port checker function==
<pre>
check_port() {
  if [[ $# -ne 2 ]]; then
    echo "Usage: check_port <HOST> <PORT>"
    echo "Example: check_port 127.0.0.1 22"
    return 1
  else
    local host=$1
    local port=$2
    (echo > "/dev/tcp/$host/$port") >/dev/null 2>&1 && echo "$host,$port,open" || echo "$host,$port,closed"
  fi
}
</pre>

[[Category:Linux]]
[[Category:ReferenceCards]]

==use netcat and dd to check network performance==
on dst:
 nc -l -vv -p 8080 >/dev/null
on src:
 dd if=/dev/zero bs=1M count=10240 | nc  dst-host 8080

==execute comands on windows server==
 # homepage: http://sourceforge.net/p/winexe/wiki/Home/
 # download: http://download.opensuse.org/repositories/home:/ahajda:/winexe/
 # download: http://repo.openpcf.org/repository/ext/openpcf/
 echo -e 'WDSUtil /Add-Device /Device:w-nb-05 /ID:74867a2a18a0 /OU:"OU=Computer,DC=domain,DC=local" \n exit' | winexe -U DOMAIN/Administrator%SuperDuper123 //10.0.0.41 cmd



