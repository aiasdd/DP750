#!/bin/bash

# Azure Databricks Lab Setup Script
# Creates an Azure Databricks Premium workspace in a randomly selected region.

set -e

# Select a region: use the first argument if provided, otherwise pick a random one
REGIONS=( koreacentral )
REGION=${1:-${REGIONS[$RANDOM % ${#REGIONS[@]}]}}

# Generate random 5-character alphanumeric string
RAND_SUFFIX=$(cat /dev/urandom | tr -dc 'a-z0-9' | head -c5)

RESOURCE_GROUP="rg-adb-$RAND_SUFFIX"
WORKSPACE_NAME="adb-ws-$RAND_SUFFIX"

echo "Installing az databricks extension..."
az config set core.collect_telemetry=no 2>/dev/null
az config set core.display_warnings=no 2>/dev/null
az config set extension.dynamic_install_allow_preview=true 2>/dev/null
az extension add --upgrade -n databricks

echo "Creating resource group $RESOURCE_GROUP in region $REGION..."
az group create \
  --name $RESOURCE_GROUP \
  --location $REGION

echo "Creating Azure Databricks Premium workspace $WORKSPACE_NAME..."
az databricks workspace create \
  --resource-group $RESOURCE_GROUP \
  --name $WORKSPACE_NAME \
  --location $REGION \
  --sku premium

echo "Installation done"
