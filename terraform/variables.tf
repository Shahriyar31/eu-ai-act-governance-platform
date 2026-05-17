# VARIABLES
# Configurable values for the infrastructure
# Change these values to deploy to different environments


variable "subscription_id" {
  description = "The Azure subscription ID where resources will be created"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group that contains all project resources"
  type        = string
  default     = "rg-eu-ai-governance"
}

variable "location" {
  description = "Azure region where resources will be deployed. Germany West Central for EU data residency compliance"
  type        = string
  default     = "Germany West Central"
}

variable "environment" {
  description = "Deployment environment — dev, staging, or prod"
  type        = string
  default     = "dev"
}

variable "storage_account_name" {
  description = "Name of the storage account for Terraform state and blob storage. Must be globally unique across all Azure, 3-24 lowercase letters and numbers only"
  type        = string
  default     = "steuaigovernance"
}

variable "key_vault_name" {
  description = "Name of the Key Vault for secrets management. Must be globally unique, 3-24 characters"
  type        = string
  default     = "kv-eu-ai-gov"
}
variable "container_registry_name" {
  description = "Name of the Azure Container Registry. Must be globally unique, alphanumeric only, 5-50 characters"
  type        = string
  default     = "euaigovernanceacr"
}

variable "db_admin_password" {
  description = "Administrator password for PostgreSQL server"
  type        = string
  sensitive   = true
}

variable "developer_ip" {
  description = "Local developer IP for PostgreSQL access during development"
  type        = string
  default     = ""
}