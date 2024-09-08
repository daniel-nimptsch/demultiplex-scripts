import argparse
from pathlib import Path
import sys
import csv


def parse_samplesheet(samplesheet_file):
    barcodes = []
    if samplesheet_file == sys.stdin:
        csv_reader = csv.reader(samplesheet_file, delimiter="\t")
    else:
        samplesheet = Path(samplesheet_file)
        with samplesheet.open(mode="r") as file:
            csv_reader = csv.reader(file, delimiter="\t")
    for row in csv_reader:
        sample_name = row[0]
        forward_barcode = row[1]
        reverse_barcode = row[2]
        forward_barcode_name = row[3]
        reverse_barcode_name = row[4]
        forward_primer = row[5]
        reverse_primer = row[6]
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
    return barcodes


def create_fasta(barcodes, output_dir, include_primers):
    """
    Create FASTA files from the samplesheet.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    forward_fasta = output_dir / "barcodes_fwd.fasta"
    reverse_fasta = output_dir / "barcodes_rev.fasta"
    forward_primer_fasta = output_dir / "primers_fwd.fasta"
    reverse_primer_fasta = output_dir / "primers_rev.fasta"

    seen_forward_barcodes = set()
    seen_reverse_barcodes = set()
    seen_forward_primers = set()
    seen_reverse_primers = set()

    with forward_fasta.open("w") as fwd_file, reverse_fasta.open("w") as rev_file, \
         forward_primer_fasta.open("w") as fwd_primer_file, reverse_primer_fasta.open("w") as rev_primer_file:
        for (
            sample_name,
            forward_barcode,
            reverse_barcode,
            forward_barcode_name,
            reverse_barcode_name,
            forward_primer,
            reverse_primer,
        ) in barcodes:
            if forward_barcode in seen_forward_barcodes:
                print(
                    f"Warning: Duplicate forward barcode {forward_barcode}. Skipping.",
                    file=sys.stderr,
                )
            else:
                seen_forward_barcodes.add(forward_barcode)
                if include_primers:
                    forward_barcode += forward_primer
                fwd_file.write(f">{forward_barcode_name}\n{forward_barcode}\n")

            if reverse_barcode in seen_reverse_barcodes:
                print(
                    f"Warning: Duplicate reverse barcode {reverse_barcode}. Skipping.",
                    file=sys.stderr,
                )
            else:
                seen_reverse_barcodes.add(reverse_barcode)
                if include_primers:
                    reverse_barcode += reverse_primer
                rev_file.write(f">{reverse_barcode_name}\n{reverse_barcode}\n")

            if not include_primers:
                if forward_primer not in seen_forward_primers:
                    seen_forward_primers.add(forward_primer)
                    fwd_primer_file.write(f">{forward_barcode_name}_primer\n{forward_primer}\n")

                if reverse_primer not in seen_reverse_primers:
                    seen_reverse_primers.add(reverse_primer)
                    rev_primer_file.write(f">{reverse_barcode_name}_primer\n{reverse_primer}\n")

    return forward_fasta, reverse_fasta, forward_primer_fasta, reverse_primer_fasta


def save_patterns(barcodes, output_dir):
    """
    Save demultiplexing patterns to a file.
    """
    patterns_file = output_dir / "patterns.txt"
    with patterns_file.open("w") as file:
        for (
            sample_name,
            forward_barcode,
            reverse_barcode,
            forward_barcode_name,
            reverse_barcode_name,
            forward_primer,
            reverse_primer,
        ) in barcodes:
            pattern_1 = f"{output_dir}/demux-{forward_barcode_name}-{reverse_barcode_name}.1.fastq.gz {sample_name}_R1.fastq.gz"
            pattern_2 = f"{output_dir}/demux-{forward_barcode_name}-{reverse_barcode_name}.2.fastq.gz {sample_name}_R2.fastq.gz"
            file.write(f"{pattern_1}\n")
            file.write(f"{pattern_2}\n")


def main():
    parser = argparse.ArgumentParser(
        description=(
            """
            Generate FASTA files from a samplesheet (TSV) containing sample
            names and barcodes. The samplesheet should be tab-delimited with
            the following format: sample name, forward barcode, reverse
            barcode, forward barcode name, reverse barcode name,forward primer
            and reverse primer.

            Additionally a patterns file is generated for the use after
            cutadapts demultiplex of paired-end reads with combinatorial dual
            indexes. The patterns file can be used as input with
            patterns_copy.py.
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
        "samplesheet",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Path to the samplesheet TSV (default: stdin)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="Directory to save the output FASTA files (default: ./)",
    )

    args = parser.parse_args()

    barcodes = parse_samplesheet(args.samplesheet)
    output_dir = Path(args.output)
    forward_fasta, reverse_fasta, forward_primer_fasta, reverse_primer_fasta = create_fasta(barcodes, output_dir, args.include_primers)
    save_patterns(barcodes, output_dir)
    
    print(f"Created barcode FASTA files: {forward_fasta}, {reverse_fasta}")
    if not args.include_primers:
        print(f"Created primer FASTA files: {forward_primer_fasta}, {reverse_primer_fasta}")


if __name__ == "__main__":
    main()
