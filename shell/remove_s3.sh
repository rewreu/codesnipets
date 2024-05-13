#!/bin/bash

# Define start and end dates
start_date="2024-01-14"
end_date="2024-04-14"

# Convert dates to seconds since the epoch
start_sec=$(date -d "$start_date" "+%s")
end_sec=$(date -d "$end_date" "+%s")

# Loop over each day
current_sec=$start_sec
while [ $current_sec -le $end_sec ]; do
  # Format current date
  current_date=$(date -d "@$current_sec" "+%d-%m-%Y")

  # Construct the S3 path
  s3_path="s3://aavvv/$current_date"

  # Delete the contents of the directory
  echo "Deleting contents of $s3_path"
  aws s3 rm $s3_path --recursive

  # Increment by one day (86400 seconds)
  current_sec=$(($current_sec + 86400))
done

echo "Deletion complete."
