#!/bin/bash

python src/parse_samplesheet_novogene.py PATH_TO_NOVOGENE_SAMPLESHEET | \
    python src/barcodes_to_fasta.py -o data/demultiplex

python src/demultiplex.py \
    PATH_TO_FWD_FASTQ \
    PATH_TO_REV_FASTQ \
    data/demultiplex/barcodes_fwd.fasta \
    data/demultiplex/barcodes_rev.fasta \
    -o data/demultiplex \
    -c

cat data/demultiplex/patterns.txt | \
    python src/patterns_copy.py -o data/demultiplex/demux_renamed

mkdir data/demultiplex/work
mv data/demultiplex/*.fastq.gz data/demultiplex/work/

bash src/dir_to_reads_tsv.sh data/demultiplex/work > data/demultiplex/cutadapt_reads.tsv
bash src/dir_to_reads_tsv.sh data/demultiplex/demux_renamed > data/demultiplex/sample_reads.tsv

python src/ampliseq_samplesheet_gen.py data/demultiplex/demux_renamed > \
    data/demultiplex/demux_renamed/sample_sheet.csv
