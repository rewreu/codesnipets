#!/bin/bash

# Define three parallel arrays
variables=("VAR1" "VAR2" "VAR3")
env_vars=("ENV1" "ENV2" "ENV3")
constants=("ConstantString1" "ConstantString2" "ConstantString3")

# Get the length of the arrays
array_length=${#variables[@]}

# Loop through the arrays by index
for (( i=0; i<array_length; i++ )); do
  # Retrieve the current environment variable's value
  current_env_var_value="${!env_vars[i]}"
  
  # Check if the environment variable is set to 'NA' or is empty
  if [[ -z "$current_env_var_value" || "$current_env_var_value" == "NA" ]]; then
    # If it is 'NA' or empty, use the constant string
    eval ${variables[i]}='${constants[i]}'
  else
    # If it exists and is not 'NA' nor empty, use the environment variable's value
    eval ${variables[i]}='${current_env_var_value}'
  fi
done

# Example to display the values
for var in "${variables[@]}"; do
  eval echo "$var is set to: \$${var}"
done
