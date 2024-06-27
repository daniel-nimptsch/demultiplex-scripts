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

cat data/demultiplex/patterns.txt | \
    python src/patterns_copy.py -o data/demultiplex/demux_renamed

mkdir data/demultiplex/work
mv data/demultiplex/*.fastq.gz data/demultiplex/work/

bash src/dir_to_reads_tsv.sh data/demultiplex/work | \
    python src/reads_stats.py > data/demultiplex/cutadapt_reads.tsv

bash src/dir_to_reads_tsv.sh data/demultiplex/demux_renamed | \
    python src/reads_stats.py > data/demultiplex/sample_reads.tsv

python src/ampliseq_samplesheet_gen.py data/demultiplex/demux_renamed > \
    data/demultiplex/demux_renamed/sample_sheet.csv
