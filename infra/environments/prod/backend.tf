terraform {
  backend "s3" {
    bucket         = "sentinel-mas-tf-state-590183890857"
    key            = "prod/terraform.tfstate"
    region         = "ap-southeast-1"
    encrypt        = true
    dynamodb_table = "sentinel-mas-tf-locks"
  }
}
