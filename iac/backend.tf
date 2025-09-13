terraform {
  backend "s3" {
    bucket = "tf-backend-s33ding-osintube"
    key    = "osintube/terraform.tfstate"
    region = "us-east-1"
  }
}
