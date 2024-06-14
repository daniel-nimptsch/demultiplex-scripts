import argparse
import csv
import os

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Samplesheet in TSV format and generate FASTA files for forward and reverse barcodes for demultiplexing with cutadapt."
    )
    parser.add_argument(
        'samplesheet', 
        type=str, 
        help='Path to the samplesheet TSV file containing sample names and barcodes'
    )

    args = parser.parse_args()

    samplesheet = args.samplesheet  # Get the samplesheet file path from arguments
    with open(samplesheet, mode='r') as file:  # Open the samplesheet file
        csv_reader = csv.reader(file, delimiter='\t')  # Read the file as a TSV
        barcodes = []  # Initialize a list to store barcodes

        for row in csv_reader:  # Iterate over each row in the TSV
            sample_name = row[0]  # First column is the sample name
            forward_barcode = row[1].split(' ')[0]  # Extract forward barcode from the second column
            reverse_barcode = row[2].split(' ')[0]  # Extract reverse barcode from the third column
            barcodes.append((sample_name, forward_barcode, reverse_barcode))  # Store the extracted values
        
        # Define the output FASTA file names
        samplesheet_base = os.path.splitext(os.path.basename(samplesheet))[0]  # Remove the path and file extension
        forward_fasta = f"{samplesheet_base}_bc_fwd.fasta"
        reverse_fasta = f"{samplesheet_base}_bc_rev.fasta"

        # Write the barcodes to the respective FASTA files
        with open(forward_fasta, 'w') as fwd_file, open(reverse_fasta, 'w') as rev_file:
            for sample_name, forward_barcode, reverse_barcode in barcodes:
                fwd_file.write(f">{sample_name}_fwd\n{forward_barcode}\n")  # Write forward barcode
                rev_file.write(f">{sample_name}_rev\n{reverse_barcode}\n")  # Write reverse barcode

if __name__ == "__main__":
    main()
