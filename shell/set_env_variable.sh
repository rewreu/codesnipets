#!/bin/bash

# Define three parallel arrays
variables=("VAR1" "VAR2" "VAR3")
env_vars=("ENV1" "ENV2" "ENV3")
constants=("ConstantString1" "ConstantString2" "ConstantString3")

# Get the length of the arrays
array_length=${#variables[@]}

# Loop through the arrays by index
for (( i=0; i<array_length; i++ )); do
  # Check if the environment variable (by index) is set and not empty
  if [ -z "${!env_vars[i]}" ]; then
    # If not set, use the constant string
    eval ${variables[i]}='${constants[i]}'
  else
    # If set, use the environment variable's value
    eval ${variables[i]}='${!env_vars[i]}'
  fi
done

# Example to display the values
for var in "${variables[@]}"; do
  eval echo "\$var is set to: \$${var}"
done
