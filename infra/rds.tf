resource "aws_db_instance" "manga_alert_postgres_db" {
  allocated_storage           = 20
  engine                      = "postgres"
  engine_version              = "16.3"
  instance_class              = "db.t3.micro"
  db_name                     = var.db_name
  identifier                  = "manga-alert-pgsql-db"
  username                    = "manga_alert_admin"
  manage_master_user_password = true
  skip_final_snapshot         = true
  publicly_accessible         = true
  vpc_security_group_ids      = [aws_security_group.manga_alert_rds_sg.id]
  db_subnet_group_name        = aws_db_subnet_group.manga_alert_rds_subnet_group.name

  storage_encrypted = true

  multi_az = false

  tags = {
    Name = "PostgreSQL Database"
  }
}
