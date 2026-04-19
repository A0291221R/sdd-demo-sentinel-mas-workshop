terraform {
  backend "s3" {
    # Replace <account-id> with your AWS account ID before running terraform init.
    # See infra/README.md for bootstrap instructions.
    bucket         = "sentinel-mas-tf-state-590183890857"
    key            = "dev/terraform.tfstate"
    region         = "ap-southeast-1"
    encrypt        = true
    dynamodb_table = "sentinel-mas-tf-locks"
  }
}
