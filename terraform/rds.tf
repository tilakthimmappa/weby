resource "aws_db_subnet_group" "rds-subnet-group" {
  name       = "rds subnet"
  subnet_ids = [aws_subnet.private-rds-subnet-1.id, aws_subnet.private-rds-subnet-2.id]
  description = "subnets"

  tags = {
    Name = "Database subnets"
  }
}




resource "aws_db_instance" "rds" {
  allocated_storage    = 20
  engine               = "postgres"
  identifier           = "weby-db"     
  engine_version       = "13"
  instance_class       = "db.t3.medium"
  name                 = "weby"
  username             = "postgres"
  password             = "postgres"
  skip_final_snapshot  = true
  publicly_accessible  = false
  db_subnet_group_name     = aws_db_subnet_group.rds-subnet-group.name
  vpc_security_group_ids   = ["${aws_security_group.rds-sg.id}"]
}