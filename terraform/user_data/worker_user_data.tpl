#!/bin/bash

# Atualizar o sistema e instalar dependências
yum update -y
yum install -y git python3

# Variáveis de ambiente
USER_QUEST="${user_quest}"
PASS_QUEST="${pass_quest}"
HOST_QUEST="${host_quest}"
HOST_WEBSOCKET="${host_websocket}"
GIT_REPO_URL="${git_repo_url}"
GIT_USERNAME="${git_username}"
GIT_TOKEN="${git_token}"

# Clonar o repositório privado usando HTTPS com token
git clone https://$GIT_USERNAME:$GIT_TOKEN@$GIT_REPO_URL /home/ec2-user/repository

# Navegar para o diretório do repositório
cd /home/ec2-user/repository

# Criar o arquivo .env com as variáveis necessárias
cat <<EOT > .env
USER_QUEST="$USER_QUEST"
PASS_QUEST="$PASS_QUEST"
HOST_QUEST="$HOST_QUEST"
HOST_WEBSOCKET="$HOST_WEBSOCKET"
EOT

# Tornar o arquivo .env seguro
chmod 600 .env

# Navegar para o diretório do worker e executar o script Python
cd src/worker

pip3 install -r requirements.txt

python3 client.py
