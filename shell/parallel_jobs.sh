#!/bin/bash

# List of arguments for --notif-date
args_list=("2025-04-01" "2025-04-02" "2025-04-03" "2025-04-04" "2025-04-05" "2025-04-06" "2025-04-07")

# Max number of parallel jobs
MAX_JOBS=6

# Function to run your command with an argument
run_command() {
    local notif_date="$1"
    echo "Starting: python run.py --mode analysis --notif-date $notif_date"
    python run.py --mode analysis --notif-date "$notif_date"
    echo "Finished: python run.py --mode analysis --notif-date $notif_date"
}

# Main loop
for date in "${args_list[@]}"; do
    # Limit concurrent jobs
    while (( $(jobs -rp | wc -l) >= MAX_JOBS )); do
        sleep 1
    done

    run_command "$date" &
done

# Wait for all background jobs
wait
echo "✅ All jobs completed."
