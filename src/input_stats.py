import argparse

# import os
# import subprocess
# import pandas as pd


def main():
    parser = argparse.ArgumentParser(
        description="Count reads in FASTA/FASTQ files and subset reads with specific adapter or primer sequences using seqkit."
    )
    parser.add_argument(
        "input_path", help="Path to the directory containing FASTA/FASTQ files"
    )
    parser.add_argument(
        "--forward_barcode", help="Path to the forward barcode FASTA file"
    )
    parser.add_argument(
        "--reverse_barcode", help="Path to the reverse barcode FASTA file"
    )
    parser.add_argument(
        "--forward_primer", help="Path to the forward primer FASTA file"
    )
    parser.add_argument(
        "--reverse_primer", help="Path to the reverse primer FASTA file"
    )
    parser.add_argument(
        "--output",
        default="read_counts.tsv",
        help="Output TSV file name (default: read_counts.tsv)",
    )

    args = parser.parse_args()

    # TODO: Implement the logic for counting reads and generating the output TSV


if __name__ == "__main__":
    main()
