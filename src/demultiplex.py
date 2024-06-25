import argparse
import os
import subprocess


def run_command(command, output_dir):
    log_file = os.path.join(output_dir, "cutadapt.log")
    with open(log_file, "w") as log:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        for line in process.stdout:
            print(line.decode(), end="")
            log.write(line.decode())
        process.wait()


def run_cutadapt(
    forward_fasta, reverse_fasta, fq_gz_1, fq_gz_2, combinatorial, output_dir
):
    """
    Execute the cutadapt command with the given parameters.
    """
    if combinatorial:
        command = (
            f"cutadapt -e 0.15 --no-indels --cores=0 "
            f"-g ^file:{forward_fasta} "
            f"-G ^file:{reverse_fasta} "
            f"-o '{output_dir}/demux-{{name1}}-{{name2}}_R1.fastq.gz' "
            f"-p '{output_dir}/demux-{{name1}}-{{name2}}_R2.fastq.gz' "
            f"{fq_gz_1} "
            f"{fq_gz_2} "
            f"--revcomp "
        )
    else:
        command = (
            f"cutadapt -e 2 --pair-adapters --cores=0 "
            f"-g ^file:{forward_fasta} "
            f"-G ^file:{reverse_fasta} "
            f"-o '{output_dir}/demux-{{name}}_R1.fastq.gz' "
            f"-p '{output_dir}/demux-{{name}}_R2.fastq.gz' "
            f"{fq_gz_1} "
            f"{fq_gz_2} "
        )

    run_command(command)


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description=(
            "Demultiplex FASTQ files using forward and reverse FASTA files containing barcodes, "
            "followed by demultiplexing with cutadapt."
        )
    )
    parser.add_argument("fq_gz_1", type=str, help="Path to the first FASTQ file (R1)")
    parser.add_argument("fq_gz_2", type=str, help="Path to the second FASTQ file (R2)")
    parser.add_argument(
        "forward_fasta",
        type=str,
        help="Path to the forward FASTA file containing barcodes",
    )
    parser.add_argument(
        "reverse_fasta",
        type=str,
        help="Path to the reverse FASTA file containing barcodes",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="Directory to save the output demultiplexed FASTQ files (default: ./)",
    )

    args = parser.parse_args()

    run_cutadapt(
        args.forward_fasta, args.reverse_fasta, args.fq_gz_1, args.fq_gz_2, args.output
    )


if __name__ == "__main__":
    main()
