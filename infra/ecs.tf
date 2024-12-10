# --- ECS Instance Role ---
# Role taken by EC2s associated with the cluster 
data "aws_iam_policy_document" "ecs_instance_assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_instance_role" {
  name               = "manga-alert-ecs-instance-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_instance_assume_role_policy.json
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role_attachment" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_role_policy" "ec2_role_policy" {
  name = "ec2_associate_eip_policy"
  role = aws_iam_role.ecs_instance_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action : "ec2:AssociateAddress",
        Effect : "Allow",
        Resource : "*"
      }
    ]
  })
}


resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "manga-alert-ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name
}

# --- ECS Task Execution Role ---
# Role used by ECS to manage instances and logs
data "aws_iam_policy_document" "ecs_task_execution_assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "manga-alert-ecs-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_assume_role_policy.json
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy_attachment" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "ecs_task_execution_additional_policy" {
  name        = "manga-alert-ecs-task-execution-additional-policy"
  description = "Additional permissions for ECS Task Execution Role"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "secretsmanager:GetSecretValue",
          "kms:Decrypt",
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParameterHistory",
          "ssm:GetParametersByPath",
          "logs:CreateLogGroup",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_additional_policy_attachment" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_task_execution_additional_policy.arn
}


# --- ECS Task Role ---
# Role taken by the application code inside the container
data "aws_iam_policy_document" "ecs_task_assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_role" {
  name               = "manga-alert-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
}

resource "aws_iam_policy" "ecs_task_policy" {
  name        = "manga-alert-ecs-task-policy"
  description = "Permissions for the ECS tasks to access AWS services"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:*",
          "secretsmanager:GetSecretValue",
          "kms:Decrypt",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "ses:*"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_role_policy_attachment" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_task_policy.arn
}



# --- ECS Launch Template ---
data "aws_ssm_parameter" "ecs_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2023/recommended/image_id"
}

resource "aws_launch_template" "manga_alert_ecs_ec2" {
  name_prefix   = "manga-alert-ecs-ec2-"
  image_id      = data.aws_ssm_parameter.ecs_ami.value
  instance_type = "t2.micro"
  credit_specification { cpu_credits = "standard" }
  iam_instance_profile { arn = aws_iam_instance_profile.ecs_instance_profile.arn }
  monitoring { enabled = true }
  network_interfaces {
    device_index                = 0
    associate_public_ip_address = true
    security_groups             = [aws_security_group.manga_alert_ecs_instances_sg.id]
  }

  key_name = "manga-alert-ec2-ssh-key"
  user_data = base64encode(<<-EOF
      #!/bin/bash
      echo "ECS_CLUSTER=${aws_ecs_cluster.manga_alert_ecs_cluster.name}" >> /etc/ecs/ecs.config
      echo 'ECS_AVAILABLE_LOGGING_DRIVERS=["json-file","awslogs"]' >> /etc/ecs/ecs.config
      REGION="eu-west-1"
      ALLOCATION_ID="${aws_eip.manga_alert_main_backend_ecs_eip.id}"
      TOKEN=$(curl --request PUT "http://169.254.169.254/latest/api/token" --header "X-aws-ec2-metadata-token-ttl-seconds: 3600")
      INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id --header "X-aws-ec2-metadata-token: $TOKEN")
      aws ec2 associate-address --instance-id $INSTANCE_ID --allocation-id $ALLOCATION_ID --region $REGION

    EOF
  )

}

#### ECS ASG
resource "aws_autoscaling_group" "manga_alert_ecs_asg" {
  vpc_zone_identifier = [
    aws_subnet.manga_alert_public_subnet1.id,
    aws_subnet.manga_alert_public_subnet2.id
  ]
  max_size         = 1
  min_size         = 0
  desired_capacity = 1

  launch_template {
    id      = aws_launch_template.manga_alert_ecs_ec2.id
    version = "$Latest"
  }

  tag {
    key                 = "AmazonECSManaged"
    value               = true
    propagate_at_launch = true
  }
}

#### ECS Cluster
resource "aws_ecs_cluster" "manga_alert_ecs_cluster" {
  name = "manga-alert-ecs-cluster"
}

resource "aws_ecs_capacity_provider" "manga_alert_ecs_capacity_provider" {
  name = "manga-alert-ecs-capacity-provider"

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.manga_alert_ecs_asg.arn

    managed_scaling {
      maximum_scaling_step_size = 1
      minimum_scaling_step_size = 1
      status                    = "ENABLED"
    }
  }
}

resource "aws_ecs_cluster_capacity_providers" "manga_alert_ecs_cluster_capacity_providers" {
  cluster_name = aws_ecs_cluster.manga_alert_ecs_cluster.name

  capacity_providers = [aws_ecs_capacity_provider.manga_alert_ecs_capacity_provider.name]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = aws_ecs_capacity_provider.manga_alert_ecs_capacity_provider.name
  }
}


#### SCRAPER TASK DEFINITION
resource "aws_ecs_task_definition" "manga_alert_scraper_ecs_definition" {
  family                   = "manga-alert-ecs-scraper"
  network_mode             = "bridge"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  cpu                      = 128
  memory                   = 128
  requires_compatibilities = ["EC2"]

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name      = "manga-alert-scraper-container"
      image     = "${aws_ecr_repository.manga_scraper_image.repository_url}:manga-scraper-image-latest"
      cpu       = 128
      memory    = 128
      essential = true

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-create-group  = "true",
          awslogs-region        = "eu-west-1"
          awslogs-group         = "manga-alert-app-scraper-logs"
          awslogs-stream-prefix = "manga-alert-app-stream-logs"
        }
      }

      environment = [
        {
          name  = "ECS_AVAILABLE_LOGGING_DRIVERS"
          value = "json-file, awslogs"
        }
      ]
    }
  ])
}


#### NOTIFIER TASK DEFINITION
resource "aws_ecs_task_definition" "manga_alert_notifier_ecs_definition" {
  family                   = "manga-alert-ecs-notifier"
  network_mode             = "bridge"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  cpu                      = 128
  memory                   = 128
  requires_compatibilities = ["EC2"]

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name      = "manga-alert-notifier"
      image     = "${aws_ecr_repository.email_notifier_image.repository_url}:email-notifier-image-latest"
      cpu       = 128
      memory    = 128
      essential = true

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-create-group  = "true",
          awslogs-region        = "eu-west-1"
          awslogs-group         = "manga-alert-app-notifier-logs"
          awslogs-stream-prefix = "manga-alert-app-stream-logs"
        }
      }

      environment = [
        {
          name  = "ECS_AVAILABLE_LOGGING_DRIVERS"
          value = "json-file, awslogs"
        }
      ]
    }
  ])
}

# MAIN_BACKEND TASK DEFINITION
resource "aws_ecs_task_definition" "manga_alert_main_backend_ecs_definition" {
  family                   = "manga-alert-ecs-main-backend"
  network_mode             = "bridge"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  cpu                      = 128
  memory                   = 128
  requires_compatibilities = ["EC2"]

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name      = "manga-alert-main-backend"
      image     = "${aws_ecr_repository.main_backend_image.repository_url}:main-backend-image-latest"
      cpu       = 128
      memory    = 128
      essential = true

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-create-group  = "true",
          awslogs-region        = "eu-west-1"
          awslogs-group         = "manga-alert-app-main-backend-logs"
          awslogs-stream-prefix = "manga-alert-app-stream-logs"
        }
      }

      environment = [
        {
          name  = "ECS_AVAILABLE_LOGGING_DRIVERS"
          value = "json-file, awslogs"
        }
      ]
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
          protocol      = "tcp"
        },
        {
          containerPort = 443
          hostPort      = 443
          protocol      = "tcp"
        },
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }
      ]
    }
  ])
}

# --- ECS Service for Main Backend ---

resource "aws_ecs_service" "manga_alert_main_backend_service" {
  name            = "manga-alert-main-backend-service"
  cluster         = aws_ecs_cluster.manga_alert_ecs_cluster.id
  task_definition = aws_ecs_task_definition.manga_alert_main_backend_ecs_definition.arn
  desired_count   = 1
  launch_type     = "EC2"

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  # Network Configuration
  # network_configuration {
  #   security_groups = [aws_security_group.manga_alert_ecs_instances_sg.id]
  #   subnets = [
  #     aws_subnet.manga_alert_public_subnet1.id,
  #     aws_subnet.manga_alert_public_subnet2.id,
  #   ]
  #   assign_public_ip = false
  # }
}
