#!/bin/bash

filter_files() {
    directory=$1
    series=$2
    start_iteration=$3
    end_iteration=$4
    master_only=$5  # New parameter to select only master files

    filtered_files=()
    for file_name in "$directory"/*; do
        if [ "$master_only" == "true" ]; then
            # Select only master files with the structure series_$series_master.h5
            if [[ $file_name =~ series_${series}_master\.h5 ]]; then
                filtered_files+=("$file_name")
            fi
        else
            # Select data files with the structure series_$series_data_00000$iteration.h5
            if [[ $file_name =~ series_${series}_data_00000([0-9]+)\.h5 ]]; then
                iteration_number=${BASH_REMATCH[1]}
                if (( iteration_number >= start_iteration && iteration_number <= end_iteration )); then
                    filtered_files+=("$file_name")
                fi
            fi
        fi
    done

    echo "${filtered_files[@]}"
}

read_series() {
    read -p "Enter the series number: " series
    if ! [[ "$series" =~ ^[0-9]+$ ]]; then
        echo "Invalid input. Please enter a valid integer."
        read_series
    fi
}

read_master_only() {
    read -p "Open master files in Albula? (yes/no): " master_choice
    if [[ "$master_choice" == "yes" ]]; then
        master_only="true"
    elif [[ "$master_choice" == "no" ]]; then
        master_only="false"
    else
        echo "Invalid input. Please enter 'yes' or 'no'."
        read_master_only
    fi
}

read_iteration_range() {
    read -p "Enter the start iteration: " start_iteration
    read -p "Enter the end iteration: " end_iteration
    if ! [[ "$start_iteration" =~ ^[0-9]+$ ]] || ! [[ "$end_iteration" =~ ^[0-9]+$ ]]; then
        echo "Invalid input. Please enter valid integers."
        read_iteration_range
    fi
}

main() {
    directory="/home/labuser/Projects/Dectris/test/temp_data"

    read_series
    read_master_only

    if [[ "$master_only" != "true" ]]; then
        read_iteration_range
    fi

    selected_files=$(filter_files "$directory" "$series" "$start_iteration" "$end_iteration" "$master_only")

    if [ -n "$selected_files" ]; then
        echo "Selected files:"
        printf '%s\n' "${selected_files[@]}"
        # Now you can launch Albula with the selected master files or data files
        albula "${selected_files[@]}"
    else
        echo "No files match the given criteria."
    fi
}

main

