#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .secrets
chmod 700 .secrets
umask 077
[ -f .secrets/password ] || openssl rand -hex 24 > .secrets/password
[ -f .secrets/keyfile ] || openssl rand -base64 512 > .secrets/keyfile
if [ ! -f .secrets/server.pem ]; then
 openssl req -x509 -newkey rsa:2048 -nodes -keyout .secrets/ca.key -out .secrets/ca.crt -days 365 -subj /CN=CollegeLabCA
 openssl req -newkey rsa:2048 -nodes -keyout .secrets/server.key -out .secrets/server.csr -subj /CN=mongo
 printf 'subjectAltName=DNS:mongo,DNS:mongo1,DNS:mongo2,DNS:mongo3,DNS:localhost,IP:127.0.0.1\nextendedKeyUsage=serverAuth,clientAuth\n' > .secrets/server.ext
 openssl x509 -req -in .secrets/server.csr -CA .secrets/ca.crt -CAkey .secrets/ca.key -CAcreateserial -out .secrets/server.crt -days 365 -extfile .secrets/server.ext
 cat .secrets/server.key .secrets/server.crt > .secrets/server.pem
 openssl req -newkey rsa:2048 -nodes -keyout .secrets/client.key -out .secrets/client.csr -subj /CN=CollegeLabClient
 printf 'extendedKeyUsage=clientAuth\n' > .secrets/client.ext
 openssl x509 -req -in .secrets/client.csr -CA .secrets/ca.crt -CAkey .secrets/ca.key -CAcreateserial -out .secrets/client.crt -days 365 -extfile .secrets/client.ext
 cat .secrets/client.key .secrets/client.crt > .secrets/client.pem
fi
