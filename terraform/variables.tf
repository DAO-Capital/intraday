variable "aws_region" {
  default = "us-east-1"
}

variable "vpc_id" {
  description = "ID da VPC"
  default     = "vpc-035f040ed55f7816f"
}

variable "subnet_id" {
  description = "ID da Subnet"
  default     = "subnet-0c58a1922d851da93"
}

variable "vpn_cidr_block" {
  description = "CIDR block da VPN para acesso às instâncias"
  type        = string
}


variable "key_pair_name" {
  default = "chaves"
}

variable "websocket_instance_type" {
  default = "t2.micro"
}

variable "worker_instance_type" {
  default = "t2.micro"
}

variable "db_instance_type" {
  default = "t3a.large"
}

# Variáveis do QuestDB
variable "user_quest" {
  description = "Nome de usuário para o QuestDB"
  type        = string
}

variable "pass_quest" {
  description = "Senha para o QuestDB"
  type        = string
  sensitive   = true
}

variable "host_websocket" {
  description = "Host do WebSocket para comunicação"
  type        = string
}

# Variáveis para o acesso ao repositório Git
variable "git_repo_url" {
  description = "URL do repositório Git"
  type        = string
}

variable "git_username" {
  description = "Nome de usuário do GitHub"
  type        = string
}

variable "git_token" {
  description = "Token de acesso pessoal do GitHub"
  type        = string
  sensitive   = true
}