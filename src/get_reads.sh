#!/bin/bash

# Get the directory path from the first argument
input_dir=$1

# Check if the directory exists
if [ ! -d "$input_dir" ]; then
    echo "Directory $input_dir does not exist."
    exit 1
fi

# Loop over all fastq.gz files in the specified directory
for file in "$input_dir"/*.fastq.gz; do
    if [ -f "$file" ]; then
        # Extract the read count
        read_count=$(zcat "$file" | grep -c '^@')

        # Print the filename and the read count, delimited by a tab
        echo -e "$file\t$read_count"
    fi
done
