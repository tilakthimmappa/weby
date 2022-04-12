resource "aws_ecr_repository" "repository" {
    name = "ecr-repo"
    image_scanning_configuration {
        scan_on_push = true
    }
}


