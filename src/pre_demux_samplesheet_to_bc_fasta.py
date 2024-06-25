import argparse
import csv
from pathlib import Path


def create_fasta_from_samplesheet(samplesheet_path, output_dir, include_primers):
    """
    Create FASTA files from the samplesheet.
    """
    samplesheet = Path(samplesheet_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with samplesheet.open(mode="r") as file:
        csv_reader = csv.reader(file, delimiter="\t")
        barcodes = parse_samplesheet(csv_reader, include_primers)

        forward_fasta = output_dir / "barcodes_fwd.fasta"
        reverse_fasta = output_dir / "barcodes_bc_rev.fasta"

        with forward_fasta.open("w") as fwd_file, reverse_fasta.open("w") as rev_file:
            for sample_name, forward_barcode, reverse_barcode in barcodes:
                fwd_file.write(f">{sample_name}\n{forward_barcode}\n")
                rev_file.write(f">{sample_name}\n{reverse_barcode}\n")

    return forward_fasta, reverse_fasta


def parse_samplesheet(csv_reader, include_primers):
    """
    Parse the samplesheet and return a list of barcodes.
    """
    barcodes = []

    for row in csv_reader:
        sample_name = row[0]
        forward_barcode = row[1].split(" ")[0] if not include_primers else row[1]
        reverse_barcode = row[2].split(" ")[0] if not include_primers else row[2]
        barcodes.append((sample_name, forward_barcode, reverse_barcode))

    return barcodes


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate FASTA files from a samplesheet (TSV) containing sample names and barcodes. "
            "The samplesheet should be tab-delimited with the following format: "
            "First column is the sample name, second column contains the forward barcode and primer "
            "(space-delimited), and the third column contains the reverse barcode and primer (space-delimited)."
        )
    )
    parser.add_argument(
        "--include-primers",
        action="store_true",
        help="Include primers in the barcodes saved to the FASTA files (default: False)",
        default=False,
    )
    parser.add_argument("samplesheet", type=str, help="Path to the samplesheet TSV")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="Directory to save the output FASTA files (default: ./)",
    )

    args = parser.parse_args()
    create_fasta_from_samplesheet(args.samplesheet, args.output, args.include_primers)


if __name__ == "__main__":
    main()

