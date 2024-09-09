#!/bin/bash

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -1|--fastq1)
            FASTQ1="$2"
            shift 2
            ;;
        -2|--fastq2)
            FASTQ2="$2"
            shift 2
            ;;
        -o|--output)
            DEMUX_PATH="$2"
            shift 2
            ;;
        -e|--error-rate)
            ERROR_RATE="$2"
            shift 2
            ;;
        --min-overlap)
            MIN_OVERLAP="$2"
            shift 2
            ;;
        --novogene-samplesheet)
            NOVOGENE_SAMPLESHEET=true
            shift
            ;;
        *)
            INPUT_SAMPLESHEET="$1"
            shift
            ;;
    esac
done

# Check for required arguments
if [ -z "$FASTQ1" ] || [ -z "$FASTQ2" ] || [ -z "$DEMUX_PATH" ] || [ -z "$INPUT_SAMPLESHEET" ]; then
    echo "Usage: $0 <input_samplesheet> -1 <fastq1> -2 <fastq2> -o <output_dir> [-e <error_rate>] [--min-overlap <min_overlap>] [--novogene-samplesheet]"
    exit 1
fi

# Demultiplex pipeline start:
INPUT_DIR=$(dirname "$FASTQ1")

echo "(1/10) Counting reads in multiplex data"
python demultiplex-scripts/src/read_counts.py "$INPUT_DIR/" \
    >"$INPUT_DIR/read_counts.tsv"

echo "(2/10) Creating directories"
mkdir -p "$DEMUX_PATH"
mkdir -p "$DEMUX_PATH/work"

echo "(3/10) Parsing samplesheet and generating barcodes"
if [ "$NOVOGENE_SAMPLESHEET" = true ]; then
    python demultiplex-scripts/src/parse_samplesheet_novogene.py \
        "$INPUT_SAMPLESHEET" \
        >"$DEMUX_PATH/input_samplesheet.tsv"
else
    cp "$INPUT_SAMPLESHEET" "$DEMUX_PATH/input_samplesheet.tsv"
fi
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
DEMUX_CMD="python demultiplex-scripts/src/demultiplex.py \
    \"$FASTQ1\" \
    \"$FASTQ2\" \
    \"$DEMUX_PATH/work/barcodes_fwd.fasta\" \
    \"$DEMUX_PATH/work/barcodes_rev.fasta\" \
    -o \"$DEMUX_PATH/work\" \
    -c"

if [ -n "$ERROR_RATE" ]; then
    DEMUX_CMD+=" -e $ERROR_RATE"
fi

if [ -n "$MIN_OVERLAP" ]; then
    DEMUX_CMD+=" --min-overlap $MIN_OVERLAP"
fi

eval $DEMUX_CMD

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
