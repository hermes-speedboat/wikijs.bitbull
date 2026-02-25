---
title: refcard
description: Daily comands that make your life easier
published: true
date: 2026-02-25T08:42:52.048Z
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
dnf -y upgrade
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

### kubectl-neat
```bash
cd /usr/local/bin
rm -f kubectl-neat
wget https://github.com/itaysk/kubectl-neat/releases/latest/download/kubectl-neat_linux_amd64.tar.gz
chmod 700 kubectl-neat
tar vxfz kubectl-neat_linux_amd64.tar.gz
rm -f LICENSE kubectl-neat_linux_amd64.tar.gz
```

### headlamp (admin ui)
* Install
```bash
kubectl config set-context --current --namespace kube-system
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/headlamp/main/kubernetes-headlamp.yaml
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
* Create creds to access the ui
```bash
kubectl -n kube-system create serviceaccount headlamp-admin
kubectl create clusterrolebinding headlamp-admin --serviceaccount=kube-system:headlamp-admin --clusterrole=cluster-admin
kubectl -n kube-system create token headlamp-admin --duration=8760h   # ~1 year
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

# Troubleshoot/Fix
## cleanup
### Remove pods that refuse to terminate
```bash
kubectl get pods -n kube-system | awk '/Terminating/ {print $1}' | \
  xargs -r kubectl delete pod -n kube-system --grace-period=0 --force
```