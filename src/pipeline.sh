#!/bin/bash

# Function to display help message
display_help() {
    cat <<EOF
Usage: $0 <input_samplesheet> <fastq1> <fastq2> [options]

Description:
This pipeline performs demultiplexing and tracks read count of input and
output files as well as read count of found barcodes and primers in
paired-end sequencing data.

Pipeline high level overview:
1. (Optional) Parsing a Novogene samplesheet with a particular format to the
    default <input_samplesheet> format (tab-delimited). This step may be skipped if
    <input_samplesheet> is already in the correct tsv format with following
    columns: sample_name, forward_barcode, reverse_barcode, forward_barcode_name,
    reverse_barcode_name, forward_primer, reverse_primer, primer_name
2. Creating barcode and primer pattern FASTA files for demultiplexing and motif
    counting, and generating a pattern file for copying demultiplexed FASTQs from
    cutadapt.
3. Counting reads in the input FASTQ files with seqkit stats.
4. (Optional) Counting motifs using seqkit locate (only if --count-motifs flag
    is used).
5. Demultiplexing with cutadapt (default: combinatorial dual indices, min
    overlap 3, max error rate 0.14).
6. Copying demultiplexed FASTQs according to the pattern file.
7. Tracking reads for both output and intermediary demultiplexed FASTQs.
8. Creating an Ampliseq-compatible samplesheet for further processing.

Note: Default demultiplexing parameters are set for barcodes of length 7.

Outputs:
    - Demultiplexed FASTQ files (stored in <output_dir>/demux_renamed/)
    - Read count reports:
        * For input FASTQs (stored in <output_dir>/input_data/)
        * For demultiplexed FASTQs (stored in <output_dir>/demux_renamed/ and
          <output_dir>/work/fastqs/)
    - Motif count report (optional, only if --count-motifs is used; stored in
        <output_dir>/input_data/)
    - Ampliseq-compatible samplesheet (stored in <output_dir>/demux_renamed/)
    - Intermediate files (barcodes, primers, patterns) (stored in
        <output_dir>/work/)

Arguments:
    <input_samplesheet>     Path to the input samplesheet
    <fastq1>                Path to the first FASTQ file (R1)
    <fastq2>                Path to the second FASTQ file (R2)

Options:
    -o, --output <dir>      Output directory for demultiplexed files (default:
                            ./data/demultiplex)
    -e, --error-rate <rate> Maximum expected error rate (default: 0.14)
    --min-overlap <int>     Minimum overlap length for adapter matching
                            (default: 3)
    --novogene-samplesheet  Use this flag if the input is a Novogene samplesheet
                            (default: false)
    -c, --combinatorial     Use combinatorial dual indexes for demultiplexing
                            (default: unique dual indices)
    --count-motifs          Execute motif counting step (default: false)
    -h, --help              Display this help message and exit

Example:
$0 input_samplesheet.tsv R1.fastq.gz R2.fastq.gz -o output_dir -e 0.1 --min-overlap 5 -c --count-motifs
EOF
}

# Set default values
DEMUX_PATH="./data/demultiplex"
ERROR_RATE=0.14
MIN_OVERLAP=3
NOVOGENE_SAMPLESHEET=false
COMBINATORIAL=false
COUNT_MOTIFS=false

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    -h | --help)
        display_help
        exit 0
        ;;
    --count-motifs)
        COUNT_MOTIFS=true
        shift
        ;;
    -o | --output)
        DEMUX_PATH="$2"
        shift 2
        ;;
    -e | --error-rate)
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
    -c | --combinatorial)
        COMBINATORIAL=true
        shift
        ;;
    *)
        if [ -z "$INPUT_SAMPLESHEET" ]; then
            INPUT_SAMPLESHEET="$1"
        elif [ -z "$FASTQ1" ]; then
            FASTQ1="$1"
        elif [ -z "$FASTQ2" ]; then
            FASTQ2="$1"
        else
            echo "Error: Unexpected argument '$1'"
            echo "Use -h or --help for usage information"
            exit 1
        fi
        shift
        ;;
    esac
done

# Check if required arguments are provided
if [ -z "$INPUT_SAMPLESHEET" ] || [ -z "$FASTQ1" ] || [ -z "$FASTQ2" ]; then
    echo "Error: Missing required arguments"
    echo "Use -h or --help for usage information"
    exit 1
fi

if [ ! -f "$INPUT_SAMPLESHEET" ]; then
    echo "Error: Input samplesheet file '$INPUT_SAMPLESHEET' does not exist."
    exit 1
fi

if [ ! -f "$FASTQ1" ]; then
    echo "Error: FASTQ1 file '$FASTQ1' does not exist."
    exit 1
fi

if [ ! -f "$FASTQ2" ]; then
    echo "Error: FASTQ2 file '$FASTQ2' does not exist."
    exit 1
fi

echo "(1/10) Creating directories"
INPUT_DIR=$(dirname "$FASTQ1")
INPUT_DATA="$DEMUX_PATH/input_data"
WORK_DIR="$DEMUX_PATH/work"

mkdir -p "$DEMUX_PATH"
mkdir -p "$WORK_DIR"
mkdir -p "$INPUT_DATA"

echo "(2/10) Counting reads in multiplex data"
python demultiplex-scripts/src/read_counts.py "$INPUT_DIR/" \
    >"$INPUT_DATA/read_counts.tsv"

echo "(3/10) Parsing samplesheet and generating barcodes"
if [ "$NOVOGENE_SAMPLESHEET" = true ]; then
    python demultiplex-scripts/src/parse_samplesheet_novogene.py \
        "$INPUT_SAMPLESHEET" \
        >"$DEMUX_PATH/input_samplesheet.tsv"
else
    cp "$INPUT_SAMPLESHEET" "$DEMUX_PATH/input_samplesheet.tsv"
fi
python demultiplex-scripts/src/barcodes_to_fasta.py -o "$WORK_DIR/" \
    <"$DEMUX_PATH/input_samplesheet.tsv"

echo "(4/10) Concatenating barcodes and primers"
cat "$WORK_DIR/barcodes_fwd.fasta" "$WORK_DIR/barcodes_rev.fasta" \
    >"$WORK_DIR/barcodes.fasta"
cat "$WORK_DIR/primers_fwd.fasta" "$WORK_DIR/primers_rev.fasta" \
    >"$WORK_DIR/primers.fasta"

if [ "$COUNT_MOTIFS" = true ]; then
    echo "(5/10) Counting motifs"
    python demultiplex-scripts/src/motif_counts.py \
        "$INPUT_DIR/" \
        "$WORK_DIR/barcodes.fasta" \
        "$WORK_DIR/primers.fasta" \
        -o "$WORK_DIR" \
        >"$INPUT_DATA/motif_counts.tsv"
else
    echo "(5/10) Skipping motif counting"
fi

echo "(6/10) Demultiplexing"
DEMUX_COMMAND="python demultiplex-scripts/src/demultiplex.py \
    \"$FASTQ1\" \
    \"$FASTQ2\" \
    \"$WORK_DIR/barcodes_fwd.fasta\" \
    \"$WORK_DIR/barcodes_rev.fasta\" \
    -o \"$WORK_DIR\" \
    -e \"${ERROR_RATE}\" \
    --min-overlap \"${MIN_OVERLAP}\""

if [ "$COMBINATORIAL" = true ]; then
    DEMUX_COMMAND+=" -c"
fi

eval "$DEMUX_COMMAND"

echo "(7/10) Copying patterns"
python demultiplex-scripts/src/patterns_copy.py -o "$DEMUX_PATH/demux_renamed" <"$WORK_DIR/patterns.txt"

echo "(8/10) Moving fastq files"
mkdir -p "$WORK_DIR/fastqs/"
mv "$DEMUX_PATH"/work/*.fastq.gz "$WORK_DIR/fastqs/"

echo "(9/10) Counting reads in demultiplexed data"
python demultiplex-scripts/src/read_counts.py "$DEMUX_PATH/demux_renamed/" \
    >"$DEMUX_PATH/demux_renamed/read_counts.tsv"
python demultiplex-scripts/src/read_counts.py "$WORK_DIR/fastqs/" \
    >"$WORK_DIR/fastqs/read_counts.tsv"

echo "(10/10) Generating ampliseq samplesheet"
python demultiplex-scripts/src/ampliseq_samplesheet_gen.py "$DEMUX_PATH/demux_renamed" \
    >"$DEMUX_PATH/demux_renamed/sample_sheet.csv"

echo "Pipeline completed successfully!"
