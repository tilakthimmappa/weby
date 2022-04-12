resource "aws_ecs_cluster" "ecs-cluster" {
  name = "ecs-cluster"
  depends_on = [
    aws_db_instance.rds
  ]
}

# Task Definition

resource "aws_ecs_task_definition" "task" {
  family = "HTTPserver"
  network_mode = "awsvpc"
  requires_compatibilities = [ "FARGATE" ]
  cpu = 256
  memory = 512
  execution_role_arn = aws_iam_role.fargate.arn

  container_definitions = jsonencode([
      {
          name = "weby-container"
          image = "${var.ECR_REPO}"
          cpu = 256
          memory = 512
          portMappings = [
              {
                  containerPort = 3000
              }
          ]
          environment =  [
            {
              name = "PG_DB",
              value = "${var.POSTGRES_DB}"
            },
            {
              name = "PG_USER",
              value = "${var.POSTGRES_USER}"
            },
            {
              name = "PG_PASS",
              value = "${var.POSTGRES_PASSWORD}"
            },
            {
              name = "PG_HOST",
              value = "${aws_db_instance.rds.address}"
            },
            {
              name = "SECRET_KEY_BASE",
              value = "${var.SECRET_KEY_BASE}"
            },
            {
              name = "RAILS_ENV",
              value = "${var.RAILS_ENV}"
            },
            {
              name = "STORAGE_HOST",
              value = "${var.STORAGE_HOST}"
            },
            {
              name = "STORAGE_BUCKET",
              value = "${var.STORAGE_BUCKET}"
            }
            ]
            logConfiguration = {
              logDriver = "awslogs",
              options = {
                awslogs-group = "weby-log",
                awslogs-stream-prefix = "weby",
                awslogs-create-group = "true",
                awslogs-region = "${var.REGION}"
              }
            }
          
      }
  ])
}

# ECS Service

resource "aws_ecs_service" "svc" {
  name = "weby-Service"
  cluster = aws_ecs_cluster.ecs-cluster.id
  task_definition = aws_ecs_task_definition.task.id
  desired_count = 1
  launch_type = "FARGATE"

  network_configuration {
    subnets = [ "${aws_subnet.public-subnets[0].id}","${aws_subnet.public-subnets[1].id}"  ]
    security_groups = [ aws_security_group.app-sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.tg-group.arn
    container_name = "weby-container"
    container_port = "3000"
  }
}