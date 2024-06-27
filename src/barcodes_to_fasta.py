import argparse
from pathlib import Path
import sys
import csv


def create_fasta(samplesheet_file, output_dir, include_primers):
    """
    Create FASTA files from the samplesheet.
    """
    barcodes = []
    if samplesheet_file == sys.stdin:
        csv_reader = csv.reader(samplesheet_file, delimiter="\t")
    else:
        samplesheet = Path(samplesheet_file)
        with samplesheet.open(mode="r") as file:
            csv_reader = csv.reader(file, delimiter="\t")
    for row in csv_reader:
        sample_name = row[0]
        forward_barcode = row[1].split(" ")[0]
        reverse_barcode = row[2].split(" ")[0]
        forward_barcode_name = row[3]
        reverse_barcode_name = row[4]
        forward_primer = row[1].split(" ")[1]
        reverse_primer = row[2].split(" ")[1]
        barcodes.append(
            (
                sample_name,
                forward_barcode,
                reverse_barcode,
                forward_barcode_name,
                reverse_barcode_name,
                forward_primer,
                reverse_primer,
            )
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    forward_fasta = output_dir / "barcodes_fwd.fasta"
    reverse_fasta = output_dir / "barcodes_rev.fasta"

    with forward_fasta.open("w") as fwd_file, reverse_fasta.open("w") as rev_file:
        for (
            sample_name,
            forward_barcode,
            reverse_barcode,
            forward_barcode_name,
            reverse_barcode_name,
            forward_primer,
            reverse_primer,
        ) in barcodes:
            if include_primers:
                forward_barcode += forward_primer
                reverse_barcode += reverse_primer
            fwd_file.write(f">{forward_barcode_name}\n{forward_barcode}\n")
            rev_file.write(f">{reverse_barcode_name}\n{reverse_barcode}\n")

    return forward_fasta, reverse_fasta


def main():
    parser = argparse.ArgumentParser(
        description=(
            """
            Generate FASTA files from a samplesheet (TSV) containing sample
            names and barcodes. The samplesheet should be tab-delimited with
            the following format: sample name, forward barcode, reverse
            barcode, forward primer and reverse primer.
            """
        )
    )
    parser.add_argument(
        "--include-primers",
        action="store_true",
        help="Include primers in the barcodes saved to the FASTA files (default: False)",
        default=False,
    )
    parser.add_argument(
        "samplesheet", nargs="?", type=argparse.FileType('r'), default=sys.stdin,
        help="Path to the samplesheet TSV (default: stdin)"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="Directory to save the output FASTA files (default: ./)",
    )

    args = parser.parse_args()

    create_fasta(args.samplesheet, args.output, args.include_primers)


if __name__ == "__main__":
    main()
