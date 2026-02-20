---
title: helpers
description: Daily comands that make your life easier
published: true
date: 2026-02-20T13:07:42.545Z
tags: helpers, kubernetes
editor: markdown
dateCreated: 2026-02-17T17:11:22.686Z
---

# k3s
## setup
### prepare os
```bash
dnf -y upgrade
dnf -y install setroubleshoot-server curl lsof wget tar vim git bash-completion

sed -i  '/swap/d' /etc/fstab
swapoff -a

systemctl disable firewalld --now
firewall-cmd --permanent --add-port=443/tcp   # ingress controller
firewall-cmd --reload
reboot
```

### install k3s
```bash
curl -sfL https://get.k3s.io | sh
grep 'kubectl completion bash' $HOME/.bashrc || echo 'source <(kubectl completion bash)' >> $HOME/.bashrc
```

## helpers
### helm
```bash
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | sh
helm completion bash > /etc/bash_completion.d/helm
grep KUBECONFIG $HOME/.bashrc || echo 'export KUBECONFIG=/etc/rancher/k3s/k3s.yaml' >> $HOME/.bashrc
```
### headlamp (admin ui)
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/headlamp/main/kubernetes-headlamp.yaml
kubectl config set-context --current --namespace kube-system
kubectl create ingress simple --rule="headlamp.app.bitbull.ch/=headlamp:80
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: headlamp
  namespace: kube-system
spec:
  ingressClassName: traefik
  rules:
  - host: admin.domain.tld
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: headlamp
            port:
              number: 80
EOF
```

# applications
## postgresql
### setup
```bash
cd ; mkdir git ; cd git
git clone https://github.com/joe-speedboat/kube.postgresql.git
cd kube.postgresql
bash deploy_postgresql.sh
```
### login
```bash
PGPASSWORD="$POSTGRES_PASSWORD" \
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

## mariadb
### setup
```bash
cd ; mkdir git ; cd git
git clone https://github.com/joe-speedboat/kube.mariadb.git
cd kube.mariadb
bash deploy_mariadb.sh
```
### login (MYSQL vars)
```bash
mariadb \
  -h 127.0.0.1 \
  -u "$MYSQL_USER" \
  -p"$MYSQL_PASSWORD" \
  "$MYSQL_DATABASE"
```

### login (MARIADB vars)
```bash
mariadb \
  -h 127.0.0.1 \
  -u "$MARIADB_USER" \
  -p"$MARIADB_PASSWORD" \
  "$MARIADB_DATABASE"
```
