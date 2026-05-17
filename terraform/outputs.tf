# OUTPUTS
# Information displayed after terraform apply completes
# These values are needed to configure other parts of the system


output "resource_group_name" {
  description = "Name of the created resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = azurerm_resource_group.main.location
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.main.name
}

output "storage_account_primary_endpoint" {
  description = "Primary blob endpoint URL of the storage account"
  value       = azurerm_storage_account.main.primary_blob_endpoint
}

output "tfstate_container_name" {
  description = "Name of the container holding Terraform state"
  value       = azurerm_storage_container.tfstate.name
}

output "key_vault_name" {
  description = "Name of the Key Vault"
  value       = azurerm_key_vault.main.name
}

output "key_vault_uri" {
  description = "URI of the Key Vault — used by applications to fetch secrets"
  value       = azurerm_key_vault.main.vault_uri
}

output "key_vault_id" {
  description = "Full resource ID of the Key Vault — used for RBAC assignments"
  value       = azurerm_key_vault.main.id
}


output "container_registry_login_server" {
  description = "Login server URL for the container registry — used by Docker to push and pull images"
  value       = azurerm_container_registry.main.login_server
}

output "container_registry_name" {
  description = "Name of the container registry"
  value       = azurerm_container_registry.main.name
}