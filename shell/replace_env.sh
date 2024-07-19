#!/bin/bash

# Example values, you can set these from your actual environment variables
VA1="us-west-2"
VA2="project-east-1"
VA3="storage-east-2"

# Check if VA1 starts with "us-west"
if [[ $VA1 == us-west* ]]; then
    # Replace '-east' with '-west' in VA2
    VA2="${VA2/-east/-west}"
    # Replace '-east' with '-west' in VA3
    VA3="${VA3/-east/-west}"
fi

# Output the results to check
echo "VA1: $VA1"
echo "VA2: $VA2"
