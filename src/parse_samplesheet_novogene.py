import argparse
import csv
from pathlib import Path


def parse_samplesheet(samplesheet_path):
    """
    Parse the samplesheet and print barcodes in TSV format.
    """

    samplesheet = Path(samplesheet_path)
    barcodes = []
    with samplesheet.open(mode="r") as file:
        csv_reader = csv.reader(file, delimiter="\t")
        for row in csv_reader:
            sample_name = row[0]
            forward_barcode = row[1].split(" ")[0]
            reverse_barcode = row[2].split(" ")[0]
            forward_barcode_name = row[3]
            reverse_barcode_name = row[4]
            primer_name = row[5]
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
                    primer_name,
                )
            )

    for barcode in barcodes:
        print("\t".join(barcode))


def main():
    parser = argparse.ArgumentParser(
        description="""
        Parse a samplesheet and print barcodes in TSV format. This is a
        specific parsing script for novogene multiplex sample sheet.
        """
    )
    parser.add_argument(
        "samplesheet_path", type=str, help="Path to the samplesheet file"
    )
    args = parser.parse_args()

    parse_samplesheet(args.samplesheet_path)


if __name__ == "__main__":
    main()
