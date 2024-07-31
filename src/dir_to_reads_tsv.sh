#!/bin/bash
#!/bin/bash

# This script generates a TSV file with read counts for each FASTQ file in the specified directory.
# Usage: bash src/dir_to_reads_tsv.sh <input_directory>
# Example: bash src/dir_to_reads_tsv.sh data/demultiplex/work

# Check for help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: bash src/dir_to_reads_tsv.sh <input_directory>"
    echo "Example: bash src/dir_to_reads_tsv.sh data/demultiplex/work"
    exit 0
fi

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
        read_count=$(zcat "$file" | rg -c '^@')
        # Print the filename and the read count, delimited by a tab
        echo -e "$file\t$read_count"
    fi
done
