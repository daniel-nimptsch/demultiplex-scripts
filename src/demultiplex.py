import argparse
import os
from pre_demux_samplesheet_to_bc_fasta import create_fasta_from_samplesheet


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
        description=(
            "Demultiplex FASTQ files using a samplesheet (TSV) to generate FASTA files "
            "containing forward and reverse barcodes, followed by demultiplexing with cutadapt. "
            "The samplesheet should be tab-delimited with the following format: "
            "First column is the sample name, second column contains the forward barcode and primer "
            "(space-delimited), and the third column contains the reverse barcode and primer (space-delimited)."
        )
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
        help=(
            "Path to the samplesheet TSV containing sample names and barcodes. "
            "The samplesheet should be tab-delimited with the following format: "
            "First column is the sample name, second column contains the forward barcode and primer "
            "(space-delimited), and the third column contains the reverse barcode and primer (space-delimited)."
        ),
    )

    args = parser.parse_args()

    forward_fasta, reverse_fasta = create_fasta_from_samplesheet(args.samplesheet, args.output)
    run_cutadapt(forward_fasta, reverse_fasta, args.fq_gz_1, args.fq_gz_2, args.output)


if __name__ == "__main__":
    main()
