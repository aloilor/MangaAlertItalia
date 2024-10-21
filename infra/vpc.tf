resource "aws_vpc" "vpc_manga_alert" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "Manga Alert VPC"
  }
}

resource "aws_internet_gateway" "manga_alert_vpc_internet_gateway" {
  vpc_id = aws_vpc.vpc_manga_alert.id

  tags = {
    Name = "Manga Alert Internet Gateway"
  }
}

### SUBNETS
resource "aws_subnet" "manga_alert_public_subnet1" {
  vpc_id                  = aws_vpc.vpc_manga_alert.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "eu-west-1a"
  tags = {
    Name = "Manga Alert Public Subnet 1"
  }
}

resource "aws_subnet" "manga_alert_public_subnet2" {
  vpc_id                  = aws_vpc.vpc_manga_alert.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "eu-west-1b"
  tags = {
    Name = "Manga Alert Public Subnet 2"
  }
}

resource "aws_route_table" "manga_alert_public_route_table" {
  vpc_id = aws_vpc.vpc_manga_alert.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.manga_alert_vpc_internet_gateway.id
  }

  tags = {
    Name = "Manga Alert Public Route Table"
  }
}

resource "aws_route_table_association" "manga_alert_public_subnet1_association" {
  subnet_id      = aws_subnet.manga_alert_public_subnet1.id
  route_table_id = aws_route_table.manga_alert_public_route_table.id
}

resource "aws_route_table_association" "manga_alert_public_subnet2_association" {
  subnet_id      = aws_subnet.manga_alert_public_subnet2.id
  route_table_id = aws_route_table.manga_alert_public_route_table.id
}

data "http" "my_ip" {
  url = "http://checkip.amazonaws.com/"
}

resource "aws_security_group" "manga_alert_ecs_instances_sg" {
  name   = "ecs-instances-security-group"
  vpc_id = aws_vpc.vpc_manga_alert.id

  ingress {
    description = "SSH access from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Manga Alert ECS Instances Security Group"
  }
}


# Security group for RDS instance
resource "aws_security_group" "manga_alert_rds_sg" {
  name        = "rds-security-group"
  description = "Security group for RDS PostgreSQL instance"
  vpc_id      = aws_vpc.vpc_manga_alert.id

  # Allow access from ECS instances
  ingress {
    description     = "PostgreSQL access from ECS tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.manga_alert_ecs_instances_sg.id]
  }

  # Allow access from your IP
  ingress {
    description = "PostgreSQL access from my IP"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
  }

  # Allow access from your IP, from Flask app port 5000
  ingress {
    description = "Flask access from my IP"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "manga_alert_rds_subnet_group" {
  name       = "manga-alert-rds-subnet-group"
  subnet_ids = [aws_subnet.manga_alert_public_subnet1.id, aws_subnet.manga_alert_public_subnet2.id]

  tags = {
    Name = "Manga Alert RDS subnet group"
  }
}

