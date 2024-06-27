from pathlib import Path
import csv


def parse_samplesheet(samplesheet_path):
    """
    Parse the samplesheet and return a list of barcodes.
    """
    barcodes = []

    samplesheet = Path(samplesheet_path)
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

    return barcodes
