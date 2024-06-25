import argparse
import csv
import os


def run_cutadapt(forward_fasta, reverse_fasta, fq_gz_1, fq_gz_2, output_dir):
    """
    Execute the cutadapt command with the given parameters.
    """
    command = (
        f"cutadapt -e 2 --pair-adapters --cores=0 "
        f"-g ^file:{forward_fasta} "
        f"-G ^file:{reverse_fasta} "
        f"-o '{output_dir}/demux-{{name}}_R1.fastq.gz' "
        f"-p '{output_dir}/demux-{{name}}_R2.fastq.gz' "
        f"{fq_gz_1} "
        f"{fq_gz_2} "
    )

    os.system(command)


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Demultiplex fastq: Samplesheet (TSV) to FASTA converter with forward and reverse barcodes with subsequent demultiplexing with cutadapt."
    )
    parser.add_argument("fq_gz_1", type=str, help="Path to the first FASTQ file (R1)")
    parser.add_argument("fq_gz_2", type=str, help="Path to the second FASTQ file (R2)")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="Directory to save the output FASTA files (default: ./)",
    )
    parser.add_argument(
        "samplesheet",
        type=str,
        help="Path to the samplesheet TSV containing sample names and barcodes. This samplesheet is expected to be a tsv. So the columns need to be tab delimied. Aditionally it is expected to have the following format: Firest column is the sample_name, second contains fwd barcode but space delimited. First is the barcode then the used primer. The same applies to  the third column but it is the rev barcode and primer.",
    )

    args = parser.parse_args()

    samplesheet = args.samplesheet  # Get the samplesheet file path from arguments
    output_dir = args.output  # Get the output directory from arguments
    os.makedirs(
        output_dir, exist_ok=True
    )  # Create the output directory if it doesn't exist

    fq_gz_1 = args.fq_gz_1  # Get the first FASTQ file path from arguments
    fq_gz_2 = args.fq_gz_2  # Get the second FASTQ file path from arguments

    with open(samplesheet, mode="r") as file:  # Open the samplesheet file
        csv_reader = csv.reader(file, delimiter="\t")  # Read the file as a TSV
        barcodes = []  # Initialize a list to store barcodes

        for row in csv_reader:  # Iterate over each row in the TSV
            sample_name = row[0]  # First column is the sample name
            forward_barcode = row[1].split(" ")[
                0
            ]  # Extract forward barcode from the second column
            reverse_barcode = row[2].split(" ")[
                0
            ]  # Extract reverse barcode from the third column
            barcodes.append(
                (sample_name, forward_barcode, reverse_barcode)
            )  # Store the extracted values

        # Define the output FASTA file names
        forward_fasta = os.path.join(output_dir, "barcodes_fwd.fasta")
        reverse_fasta = os.path.join(output_dir, "barcodes_bc_rev.fasta")

        # Write the barcodes to the respective FASTA files
        with open(forward_fasta, "w") as fwd_file, open(reverse_fasta, "w") as rev_file:
            for sample_name, forward_barcode, reverse_barcode in barcodes:
                fwd_file.write(
                    f">{sample_name}\n{forward_barcode}\n"
                )  # Write forward barcode
                rev_file.write(
                    f">{sample_name}\n{reverse_barcode}\n"
                )  # Write reverse barcode

        # Run cutadapt with the generated FASTA files and provided FASTQ files
        run_cutadapt(forward_fasta, reverse_fasta, fq_gz_1, fq_gz_2, output_dir)


if __name__ == "__main__":
    main()
