# Configure the AWS provider
provider "aws" {
  region = var.aws_region
}

# VPC and Subnet for EC2 Instances, when using, delete mock_vpc and mock_subnet and use existing VPC and Subnet
resource "aws_vpc" "mock_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "Mock VPC"
  }
}

resource "aws_subnet" "mock_subnet" {
  vpc_id            = aws_vpc.mock_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a" 
  tags = {
    Name = "Mock Subnet"
  }
}

data "aws_vpc" "existing_vpc" {
  id = aws_vpc.mock_vpc.id
}

data "aws_subnet" "existing_subnet" {
  id = aws_subnet.mock_subnet.id
}


# Security Group for Worker Instance
resource "aws_security_group" "worker_sg" {
  name        = "worker_sg"
  description = "Security group for Worker instance"
  vpc_id      = data.aws_vpc.existing_vpc.id

  # Ingress Rules
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.vpn_cidr_block]  # Acesso via VPN
    description = "Allow SSH access from VPN"
  }

  # Egress Rules
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # Permite todo o tráfego de saída
    description = "Allow all outbound traffic"
  }

  tags = {
    Name = "Worker Security Group"
  }
}

# Security Group for QuestDB Instance
resource "aws_security_group" "questdb_sg" {
  name        = "questdb_sg"
  description = "Security group for QuestDB instance"
  vpc_id      = data.aws_vpc.existing_vpc.id

  # Ingress Rules
  ingress {
    from_port   = 9009
    to_port     = 9009
    protocol    = "udp"
    cidr_blocks = [var.vpn_cidr_block]
    description = "Allow UDP traffic on port 9009 from VPN"
  }

  ingress {
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = [var.vpn_cidr_block]
    description = "Allow TCP traffic on port 9000 from VPN"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.vpn_cidr_block]
    description = "Allow HTTP traffic from VPN"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.vpn_cidr_block]
    description = "Allow SSH access from VPN"
  }

  ingress {
    from_port   = 8812
    to_port     = 8812
    protocol    = "tcp"
    cidr_blocks = [var.vpn_cidr_block]
    description = "Allow TCP traffic on port 8812 from VPN"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpn_cidr_block]
    description = "Allow HTTPS traffic from VPN"
  }

  # Egress Rules
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name = "QuestDB Security Group"
  }
}

# IAM Role for EC2 Instances (Optional)
resource "aws_iam_role" "ec2_role" {
  name = "ec2_instance_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

# IAM Policy Attachment (Optional)
resource "aws_iam_role_policy_attachment" "ec2_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"  # Ajuste conforme necessário
}

# Instance Profile
resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2_instance_profile"
  role = aws_iam_role.ec2_role.name
}

# User Data Scripts
data "template_file" "quest_user_data" {
  template = file("${path.module}/user_data/quest_user_data.tpl")

  vars = {
    user_quest = var.user_quest
    pass_quest = var.pass_quest
  }
}

data "template_file" "worker_user_data" {
  template = file("${path.module}/user_data/worker_user_data.tpl")

  vars = {
    user_quest   = var.user_quest
    pass_quest   = var.pass_quest
    host_quest   = aws_instance.questdb_instance.private_ip
    git_repo_url = var.git_repo_url
    git_username = var.git_username
    git_token    = var.git_token
  }
}

# EC2 Instance for Worker
resource "aws_instance" "worker_instance" {
  ami                         = "ami-0c02fb55956c7d316"  # Verifique se este AMI ID é válido na sua região
  instance_type               = var.worker_instance_type
  subnet_id                   = data.aws_subnet.existing_subnet.id
  vpc_security_group_ids      = [aws_security_group.worker_sg.id]
  key_name                    = var.key_pair_name
  iam_instance_profile        = aws_iam_instance_profile.ec2_instance_profile.name
  associate_public_ip_address = true

  user_data = data.template_file.worker_user_data.rendered

  tags = {
    Name = "Worker Instance"
  }
}

# EC2 Instance for QuestDB
resource "aws_instance" "questdb_instance" {
  ami                         = "ami-011624f579af10f63"  # Verifique se este AMI ID é válido na sua região
  instance_type               = var.db_instance_type
  subnet_id                   = data.aws_subnet.existing_subnet.id
  vpc_security_group_ids      = [aws_security_group.questdb_sg.id]
  key_name                    = var.key_pair_name
  iam_instance_profile        = aws_iam_instance_profile.ec2_instance_profile.name
  associate_public_ip_address = true

  user_data = data.template_file.quest_user_data.rendered

  tags = {
    Name = "QuestDB Instance"
  }
}
