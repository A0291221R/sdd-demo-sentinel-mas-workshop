variable "environment" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "rds_sg_id" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t3.micro"
}

variable "deletion_protection" {
  description = "Enable deletion protection on the RDS instance."
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot on RDS instance deletion."
  type        = bool
  default     = true
}

variable "final_snapshot_identifier" {
  description = "Identifier for the final snapshot when skip_final_snapshot is false."
  type        = string
  default     = ""
}
