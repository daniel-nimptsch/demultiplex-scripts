import argparse

# import os
# import subprocess
# import pandas as pd


def main():
    parser = argparse.ArgumentParser(
        description="Count reads in FASTA/FASTQ files and subset reads with specific adapter or primer sequences using seqkit."
    )
    _ = parser.add_argument(
        "input_path", help="Path to the directory containing FASTA/FASTQ files"
    )
    _ = parser.add_argument(
        "--forward_barcode", help="Path to the forward barcode FASTA file"
    )
    _ = parser.add_argument(
        "--reverse_barcode", help="Path to the reverse barcode FASTA file"
    )
    _ = parser.add_argument(
        "--forward_primer", help="Path to the forward primer FASTA file"
    )
    _ = parser.add_argument(
        "--reverse_primer", help="Path to the reverse primer FASTA file"
    )
    _ = parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output TSV file path. If not specified, output will be printed to stdout.",
    )

    args = parser.parse_args()

    # TODO: Implement the logic for counting reads and generating the output TSV


if __name__ == "__main__":
    main()
