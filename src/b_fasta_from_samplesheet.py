import argparse
import csv

def main():
    parser = argparse.ArgumentParser(description="Process a samplesheet in TSV format.")
    parser.add_argument('samplesheet', type=str, help='Path to the samplesheet TSV file')

    args = parser.parse_args()

    samplesheet = args.samplesheet
    with open(samplesheet, mode='r') as file:
        csv_reader = csv.reader(file, delimiter='\t')
        barcodes = []
        for row in csv_reader:
            sample_name = row[0]
            forward_barcode = row[1].split(' ')[0]
            reverse_barcode = row[2].split(' ')[0]
            barcodes.append((sample_name, forward_barcode, reverse_barcode))
        
        for sample_name, forward_barcode, reverse_barcode in barcodes:
            print(f"Sample: {sample_name}, Forward Barcode: {forward_barcode}, Reverse Barcode: {reverse_barcode}")

if __name__ == "__main__":
    main()
