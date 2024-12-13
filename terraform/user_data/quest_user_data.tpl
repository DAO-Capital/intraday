#!/bin/bash

# Variáveis de ambiente
USERNAME="${user_quest}"
PASSWORD="${pass_quest}"

# Caminhos (ajuste conforme necessário)
QUESTDB_HOME='/root/.questdb'
CONFIG_FILE="$QUESTDB_HOME/conf/server.conf"
USERS_FILE="$QUESTDB_HOME/conf/auth/users.txt"

# Certifique-se de que os diretórios de configuração existem
mkdir -p "$(dirname "$CONFIG_FILE")"
mkdir -p "$(dirname "$USERS_FILE")"

# Configurar segurança no QuestDB
if grep -q '^http.security.enabled' "$CONFIG_FILE"; then
  sed -i 's/^http.security.enabled=.*/http.security.enabled=true/' "$CONFIG_FILE"
else
  echo "http.security.enabled=true" >> "$CONFIG_FILE"
fi

if grep -q '^http.security.readonly' "$CONFIG_FILE"; then
  sed -i 's/^http.security.readonly=.*/http.security.readonly=false/' "$CONFIG_FILE"
else
  echo "http.security.readonly=false" >> "$CONFIG_FILE"
fi

# Criar arquivo de usuários com as credenciais fornecidas
echo "$USERNAME:$PASSWORD" > "$USERS_FILE"

# Reiniciar o QuestDB para aplicar as mudanças
systemctl restart questdb
