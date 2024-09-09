#!/bin/bash

# Modify these variables
FASTQ1="path/to/fastq1"
FASTQ2="path/to/fastq1"
DEMUX_PATH="path/to/output/dir"

# Demultiplex pipeline start:
INPUT_DIR=$(dirname "$FASTQ1")

echo "(1/10) Counting reads in multiplex data"
python demultiplex-scripts/src/read_counts.py "$INPUT_DIR/" \
    >"$INPUT_DIR/read_counts.tsv"

echo "(2/10) Creating directories"
mkdir -p "$DEMUX_PATH"
mkdir -p "$DEMUX_PATH/work"

echo "(3/10) Parsing samplesheet and generating barcodes"
python demultiplex-scripts/src/parse_samplesheet_novogene.py \
    "$INPUT_DIR/multiplex_samplesheet.tsv" \
    >"$DEMUX_PATH/input_samplesheet.tsv"
python demultiplex-scripts/src/barcodes_to_fasta.py -o "$DEMUX_PATH/work/" \
    <"$DEMUX_PATH/input_samplesheet.tsv"

echo "(4/10) Concatenating barcodes and primers"
cat "$DEMUX_PATH/work/barcodes_fwd.fasta" "$DEMUX_PATH/work/barcodes_rev.fasta" \
    >"$DEMUX_PATH/work/barcodes.fasta"
cat "$DEMUX_PATH/work/primers_fwd.fasta" "$DEMUX_PATH/work/primers_rev.fasta" \
    >"$DEMUX_PATH/work/primers.fasta"

echo "(5/10) Counting motifs"
python demultiplex-scripts/src/motif_counts.py \
    "$INPUT_DIR/" \
    "$DEMUX_PATH/work/barcodes.fasta" \
    "$DEMUX_PATH/work/primers.fasta" \
    -o "$DEMUX_PATH/work" \
    >"$INPUT_DIR/motif_counts.tsv"

echo "(6/10) Demultiplexing"
python demultiplex-scripts/src/demultiplex.py \
    "$FASTQ1" \
    "$FASTQ2" \
    "$DEMUX_PATH/work/barcodes_fwd.fasta" \
    "$DEMUX_PATH/work/barcodes_rev.fasta" \
    -o "$DEMUX_PATH/work" \
    -c

echo "(7/10) Copying patterns"
python demultiplex-scripts/src/patterns_copy.py -o "$DEMUX_PATH/demux_renamed" <"$DEMUX_PATH/work/patterns.txt"

echo "(8/10) Moving fastq files"
mkdir -p "$DEMUX_PATH/work/fastqs/"
mv "$DEMUX_PATH"/work/*.fastq.gz "$DEMUX_PATH/work/fastqs/"

echo "(9/10) Counting reads in demultiplexed data"
python demultiplex-scripts/src/read_counts.py "$DEMUX_PATH/demux_renamed/" \
    >"$DEMUX_PATH/demux_renamed/read_counts.tsv"
python demultiplex-scripts/src/read_counts.py "$DEMUX_PATH/work/fastqs/" \
    >"$DEMUX_PATH/work/fastqs/read_counts.tsv"

echo "(10/10) Generating ampliseq samplesheet"
python demultiplex-scripts/src/ampliseq_samplesheet_gen.py "$DEMUX_PATH/demux_renamed" \
    >"$DEMUX_PATH/demux_renamed/sample_sheet.csv"

echo "Pipeline completed successfully!"
