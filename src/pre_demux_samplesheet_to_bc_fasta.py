import argparse
from pathlib import Path


def create_fasta(barcodes, output_dir, include_primers):
    """
    Create FASTA files from the samplesheet.
    """
    output_dir = Path(output_dir)
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
