#!/usr/bin/bash

python src/parse_samplesheet_novogene.py docs/sample_sheet_agr.tsv | \
    python src/barcodes_to_fasta.py -o data/demultiplex

python src/demultiplex.py \
    data/multiplex/AgroSoil_1_FKDN240147590-1A_H7HKJDRX5_L2_1.fq.gz \
    data/multiplex/AgroSoil_1_FKDN240147590-1A_H7HKJDRX5_L2_2.fq.gz \
    data/demultiplex/barcodes_fwd.fasta \
    data/demultiplex/barcodes_rev.fasta \
    -o data/demultiplex \
    -c

cat data/demultiplex/patterns.txt | python src/rename_files.py

bash src/get_reads_from_fastqs_in_dir.sh data/demultiplex | \
    python src/reads_stats_from_tsv.py > data/demultiplex/cutadapt_reads.tsv

bash src/get_reads_from_fastqs_in_dir.sh data/demultiplex/renamed | \
    python src/reads_stats_from_tsv.py > data/demultiplex/sample_reads.tsv

python src/ampliseq_samplesheet_gen.py data/demultiplex/renamed > \
    data/demultiplex/renamed/sample_sheet.csv

python src/ampliseq_samplesheet_gen.py data/demultiplex/renamed > samplesheet.csv
