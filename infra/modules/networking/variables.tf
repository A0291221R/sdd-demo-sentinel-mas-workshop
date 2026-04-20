variable "environment" {
  type = string
}

variable "nat_gateway_count" {
  description = "Number of NAT gateways (1 for dev cost savings, 2 for prod AZ redundancy)."
  type        = number
  default     = 1
}
