#!/bin/bash

# Loop over all fastq.gz files in the directory
for file in *.fastq.gz; do
    if [ -f "$file" ]; then
        # Extract the read count
        read_count=$(zcat "$file" | grep -c '^@')

        # Print the filename and the read count
        echo "$file: $read_count"
    fi
done
