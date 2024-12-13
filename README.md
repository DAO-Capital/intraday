# Projeto de Arquitetura para Fluxo de Dados de Alta Frequência e Modelagem de Estratégias de Investimento

## 1. Introdução

Este projeto foi desenvolvido como parte do trabalho de conclusão de curso, visando a criação de uma arquitetura robusta e escalável para o processamento de dados de alta frequência (High-Frequency Data - HFD) de ativos financeiros. O objetivo principal é sustentar a modelagem de estratégias de compra e venda de ações em alta frequência para a DAO Capital, uma gestora de investimentos, utilizando técnicas avançadas de processamento de dados e Machine Learning.

O projeto inclui a construção de uma infraestrutura para a extração, transformação e carregamento (ETL) de grandes volumes de dados, a implementação de um banco de dados otimizado para séries temporais, e o desenvolvimento de modelos preditivos para estratégias de investimento baseados em sinais financeiros e algoritmos de aprendizado de máquina.

## 2. Sumário

1. [Introdução](#1-introdução)
2. [Descrição do Projeto](#3-descrição-do-projeto)
3. [Arquitetura do Sistema](#4-arquitetura-do-sistema)
4. [Instalação e Configuração](#5-instalação-e-configuração)
5. [Execução do Projeto](#6-execução-do-projeto)
   1. [Provisionando a Infraestrutura com Terraform](#61-provisionando-a-infraestrutura-com-terraform)
   2. [Configurando as Variáveis de Ambiente](#62-configurando-as-variáveis-de-ambiente)
   3. [Aplicando a Configuração com Terraform](#63-aplicando-a-configuração-com-terraform)
   4. [Executando o QuestDB](#64-executando-o-questdb)
   5. [Executando o Cliente ETL](#65-executando-o-cliente-etl)
   6. [Executando as Análises](#66-executando-as-análises)
6. [Estrutura do Projeto](#7-estrutura-do-projeto)
7. [Colaboradores](#8-colaboradores)
8. [Referências](#9-referências)

## 3. Descrição do Projeto

A manipulação de dados de alta frequência requer uma infraestrutura capaz de lidar com grandes volumes de informações em curtos períodos de tempo. Para atender a essa necessidade, o projeto foi estruturado em três pilares principais:

1. **Pipeline de Dados em Python**: Desenvolvimento de scripts e aplicações em Python para a extração, transformação e carregamento (ETL) dos dados, garantindo eficiência e escalabilidade no processamento.

2. **Armazenamento Otimizado com QuestDB**: Utilização do QuestDB, um banco de dados de alto desempenho otimizado para séries temporais, permitindo o armazenamento e recuperação eficientes de grandes volumes de dados.

3. **Modelagem e Análise de Dados**: Implementação de modelos de Machine Learning e análise de sinais financeiros para a criação de estratégias de investimento, incluindo modelos preditivos e análise de indicadores técnicos.

## 4. Arquitetura do Sistema

A arquitetura do sistema foi projetada para garantir a escalabilidade e eficiência no processamento dos dados de alta frequência. Os componentes principais incluem:

- **Worker**: Responsável por executar o Cliente ETL. O Worker conecta-se ao banco de dados QuestDB, realiza a transformação necessária e insere os dados no QuestDB. O Worker foi otimizado para lidar com grandes volumes de dados, garantindo a integridade e velocidade no processo de ETL.

- **QuestDB**: Banco de dados de séries temporais utilizado para armazenar os dados de alta frequência. O QuestDB foi escolhido devido ao seu alto desempenho e facilidade de integração com aplicações em Python. Utilizamos uma Amazon Machine Image (AMI) já configurada com o QuestDB, facilitando a implantação na AWS.

- **Análises e Modelagem**: Conjunto de notebooks Jupyter contendo a implementação de modelos preditivos, análise de sinais financeiros e estratégias de investimento. Foram utilizados modelos como CatBoost, XGBoost e Random Forest, além de indicadores técnicos como Bandas de Bollinger, RSI e Momentum.

## 5. Instalação e Configuração

### 5.1. Pré-requisitos

- **Conta na AWS**: Necessária para provisionar a infraestrutura utilizando os arquivos Terraform.
- **AMI QuestDB**: Necessário contratar a AMI disponibilizada pelo QuestDB no Amazon Marketplace. Facilita muito algumas configurações necessárias para o QuestDB Enterprise. 

  Nome: QuestDB: high-performance open source SQL database for time series
- **Terraform**: Para provisionamento da infraestrutura na nuvem.
- **Git**
- **Python 3.8 ou superior**
- **pip** (gerenciador de pacotes do Python)
- **Virtualenv** (opcional, mas recomendado)

### 5.2. Clone do Repositório

Para iniciar, clone o repositório do projeto em sua máquina local:

```bash
git clone https://github.com/pfeinsper/24-b-dao.git
cd seu-repositorio
```

### 5.3. Configuração de Variáveis

1. Edite o arquivo `terraform.tfvars` com as variáveis necessárias, incluindo credenciais e endereços de rede:

   ```hcl
   user_quest     = "seu_usuario_quest"
   pass_quest     = "sua_senha_quest"
   host_websocket     = "endereco_websocket"
   git_repo_url   = "https://github.com/seu_usuario/seu_repositorio.git"
   git_username   = "seu_usuario_github"
   git_token      = "seu_token_de_acesso_pessoal"
   vpn_cidr_block      = "ip de sua VPN"
   ```

2. Certifique-se de que as credenciais do AWS CLI estejam configuradas corretamente para permitir o acesso aos recursos AWS.

---

## 6. Execução do Projeto

O projeto é executado dentro das instâncias AWS que serão provisionadas utilizando os arquivos Terraform. As instruções a seguir detalham como provisionar a infraestrutura e executar os componentes automaticamente através dos scripts de *user data*.

### 6.1. Provisionando a Infraestrutura com Terraform

Inicialize o Terraform para baixar os plugins necessários:

```bash
terraform init
```

Em seguida, visualize o plano de execução:

```bash
terraform plan
```

E aplique a configuração:

```bash
terraform apply
```

Confirme a aplicação digitando `yes` quando solicitado.

---

### 6.2. Executando o QuestDB

O QuestDB já está pré-instalado e configurado na instância provisionada. Para verificar se o QuestDB está em execução corretamente, acesse o painel de controle via navegador utilizando o endereço IP público da instância:

```bash
http://<IP_PÚBLICO_DA_INSTÂNCIA_QUESTDB>:9000
```

---

### 6.3. Executando o Cliente ETL

O Cliente ETL é configurado automaticamente no provisionamento e começa a rodar na instância do Worker. Ele realiza as seguintes ações:

1. **Clona o Repositório Git Privado:**
   - Utiliza as credenciais fornecidas para clonar o repositório.

2. **Cria o Arquivo `.env`:**
   - Define as variáveis de ambiente necessárias para a conexão com o QuestDB.

3. **Executa o Script Python `client.py`:**
   - Inicia o processo de ETL para receber, processar e armazenar os dados no QuestDB.


---

## 7. Estrutura do Projeto

Abaixo está uma visão detalhada e precisa da estrutura de diretórios e arquivos do projeto:

```plaintext
├── data/
├── notebooks/
│   ├── signals/
│   │   ├── ML Models/
│   │   │   ├── Categorical Models Results/
│   │   │   ├── Categorical-Models/
│   │   │   ├── Non-Categorical Models/
│   │   │   ├── Non-Categorical Models Results/
│   │   │   ├── feature_importances.png
│   │   │   ├── results.png
│   │   │   ├── return_prediction_categorical.ipynb
│   │   │   └── return_prediction_non_categorical.ipynb
│   ├── analytics_momentum_factor.ipynb
├── src/
│   ├── websocket/
│   │   ├── server_hf.py
│   │   ├── server.py
│   │   ├── server_crypto.py
│   │   ├── server_time.py
│   └── worker/
│       ├── client.py
│       └── extract.py
├── terraform/
│   ├── user_data/
│   │   ├── quest_user_data.tpl
│   │   ├── worker_user_data.tpl
│   ├── main.tf
│   ├── output.tf
│   ├── terraform.tfvars
│   ├── variables.tf
├── README.md
├── requirements.txt
```

## 8. Colaboradores

Este projeto foi desenvolvido pelos seguintes membros:

- **Felipe Maluli de Carvalho Dias**
- **Guilherme dos Santos Martins**
- **Marlon Silva Pereira**
- **Orientador**: Prof. Maciel Calebe Vidal

- **Mentor**: Matteo Iannoni

- **Coordenador Capstone**: Prof. Dr. Luciano P. Soares

## 9. Referências

### Bancos de Dados
- [Documentação do QuestDB](https://questdb.io/docs/)

### Infraestrutura como Código (IaC)
- [Documentação do Terraform](https://developer.hashicorp.com/terraform/docs)

### Contêineres
- [Documentação do Docker](https://docs.docker.com/)

### Linguagem de Programação
- [Documentação do Python](https://docs.python.org/3/)

### Análise de Dados
- [Documentação do Pandas](https://pandas.pydata.org/docs/)

### Aprendizado de Máquina
- [Documentação do Scikit-Learn](https://scikit-learn.org/stable/documentation.html)
- [Documentação do CatBoost](https://catboost.ai/en/docs/)
- [Documentação do XGBoost](https://xgboost.readthedocs.io/en/stable/)

### Websockets
- [WebSockets](https://websockets.readthedocs.io/en/stable/)
