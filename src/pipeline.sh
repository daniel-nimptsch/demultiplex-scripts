#!/bin/bash

# Function to display help message
display_help() {
    echo "Usage: $0 <input_samplesheet> <fastq1> <fastq2> [options]"
    echo
    echo "Description:"
    echo "  This pipeline performs demultiplexing and analysis of paired-end sequencing data."
    echo "  The process includes:"
    echo "  1. (Optional) Parsing the Novogene samplesheet to the default INPUT_SAMPLESHEET format (tab-delimited)."
    echo "     This step may be skipped if INPUT_SAMPLESHEET is already in the correct format:"
    echo "     sample_id<tab>barcode_fwd<tab>barcode_rev<tab>primer_fwd<tab>primer_rev"
    echo "  2. Creating barcode and primer FASTA files for demultiplexing and motif counting,"
    echo "     and generating a pattern file for copying demultiplexed FASTQs."
    echo "  3. Counting reads in the input FASTQ files."
    echo "  4. Counting motifs using seqkit."
    echo "  5. Demultiplexing with cutadapt (default: combinatorial dual indices, min overlap 3, max error rate 0.14)."
    echo "  6. Copying demultiplexed FASTQs according to the pattern file."
    echo "  7. Tracking reads for both output and intermediary demultiplexed FASTQs."
    echo "  8. Creating an Ampliseq-compatible samplesheet for further processing."
    echo
    echo "  Note: Default demultiplexing parameters are set for barcodes of length 7. Adjust as needed."
    echo
    echo "Outputs:"
    echo "  - Demultiplexed FASTQ files"
    echo "  - Read count reports for input and demultiplexed FASTQs"
    echo "  - Motif count report"
    echo "  - Ampliseq-compatible samplesheet"
    echo "  - Intermediate files (barcodes, primers, patterns)"
    echo
    echo "Arguments:"
    echo "  <input_samplesheet>    Path to the input samplesheet"
    echo "  <fastq1>               Path to the first FASTQ file (R1)"
    echo "  <fastq2>               Path to the second FASTQ file (R2)"
    echo
    echo "Options:"
    echo "  -o, --output <dir>     Output directory for demultiplexed files (default: ./data/demultiplex)"
    echo "  -e, --error-rate <rate> Maximum expected error rate (default: 0.14)"
    echo "  --min-overlap <int>    Minimum overlap length for adapter matching (default: 3)"
    echo "  --novogene-samplesheet Use this flag if the input is a Novogene samplesheet"
    echo "  -c, --combinatorial    Use combinatorial dual indexes for demultiplexing"
    echo "  -h, --help             Display this help message and exit"
    echo
    echo "Example:"
    echo "  $0 input_samplesheet.tsv R1.fastq.gz R2.fastq.gz -o output_dir -e 0.1 --min-overlap 5 -c"
}

# Set default values
DEMUX_PATH="./data/demultiplex"
ERROR_RATE=0.14
MIN_OVERLAP=3
NOVOGENE_SAMPLESHEET=false
COMBINATORIAL=false

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    -h | --help)
        display_help
        exit 0
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
DEMUX_COMMAND="python demultiplex-scripts/src/demultiplex.py \
    \"$FASTQ1\" \
    \"$FASTQ2\" \
    \"$DEMUX_PATH/work/barcodes_fwd.fasta\" \
    \"$DEMUX_PATH/work/barcodes_rev.fasta\" \
    -o \"$DEMUX_PATH/work\" \
    -e \"${ERROR_RATE}\" \
    --min-overlap \"${MIN_OVERLAP}\""

if [ "$COMBINATORIAL" = true ]; then
    DEMUX_COMMAND+=" -c"
fi

eval $DEMUX_COMMAND

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
