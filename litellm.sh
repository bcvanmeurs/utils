#!/bin/bash

# List of environment options
environments=("ds-lab-2" "engine-dev-2" "inference-dev-1" "engine-stage-1" "engine-geopol" "inference-1" "prod-mt-01")

# Function to display the menu
function show_menu {
	echo "Please select an environment:"
	for i in "${!environments[@]}"; do
		echo "$((i + 1)). ${environments[$i]}"
	done
}

# Function to execute kubectx with the selected environment
function execute_kubectx {
	local env=$1
	echo "Switching to environment: $env"
	kubectx $env
}

# Function to get the secret and print the user and password
function get_and_print_secret {
	local secret=$(kubectl get secret -n litellm litellm-proxy-masterkey -o yaml | yq .data.masterkey | base64 -d)
	echo ""
	echo "Credentials for the environment:"
	echo "user: admin"
	echo "password: $secret"
}

# Display the menu
show_menu

# Read user input
read -p "Enter the number corresponding to your choice: " choice

# Validate user input and execute the corresponding kubectx command
if [[ $choice -ge 1 && $choice -le ${#environments[@]} ]]; then
	selected_env=${environments[$((choice - 1))]}
	execute_kubectx $selected_env

	# Get the secret and print the user and password
	get_and_print_secret
else
	echo "Invalid choice. Please run the script again and select a valid option."
	exit 1
fi

echo "Opening the browser..."
open http://localhost:4000/ui/

echo ""
echo "Starting port-forwarding..."
kubectl port-forward -n litellm svc/litellm-proxy 4000:4000
