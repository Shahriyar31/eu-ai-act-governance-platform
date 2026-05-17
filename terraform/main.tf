# TERRAFORM BLOCK
# Defines which version of Terraform and which providers to use

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}


# PROVIDER BLOCK
# Tells Terraform how to connect to Azure


provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
}


# RESOURCE GROUP
# The container for all project resources
# Everything we create in Azure will live inside this


resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    project     = "eu-ai-act-governance"
    environment = var.environment
    managed_by  = "terraform"
  }
}


# STORAGE ACCOUNT
# Used for:
# 1. Terraform remote state storage
# 2. PDF compliance report storage (later)


resource "azurerm_storage_account" "main" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  blob_properties {
    versioning_enabled = true
  }

  tags = {
    project     = "eu-ai-act-governance"
    environment = var.environment
    managed_by  = "terraform"
  }
}


# STORAGE CONTAINER
# The folder inside the Storage Account
# that holds the Terraform state file


resource "azurerm_storage_container" "tfstate" {
  name                  = "tfstate"
  storage_account_id    = azurerm_storage_account.main.id
  container_access_type = "private"
}


# KEY VAULT
# Stores all secrets — API keys, passwords, encryption keys
# Nothing sensitive ever goes in code or GitHub


data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                = var.key_vault_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  soft_delete_retention_days = 7
  purge_protection_enabled   = false

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get",
      "List",
      "Set",
      "Delete",
      "Purge"
    ]
  }

  tags = {
    project     = "eu-ai-act-governance"
    environment = var.environment
    managed_by  = "terraform"
  }
}