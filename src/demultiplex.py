import argparse
import os
import subprocess


def run_command(command: str, output_dir: str) -> None:
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
    forward_fasta: str,
    reverse_fasta: str,
    fq_gz_1: str,
    fq_gz_2: str,
    combinatorial: bool,
    output_dir: str,
    error_rate: float | None,
    min_overlap: int | None,
):
    """
    Execute the cutadapt command with the given parameters.

    Args:
        forward_fasta (str): Path to the forward FASTA file containing barcodes.
        reverse_fasta (str): Path to the reverse FASTA file containing barcodes.
        fq_gz_1 (str): Path to the first FASTQ file (R1).
        fq_gz_2 (str): Path to the second FASTQ file (R2).
        combinatorial (bool): Whether to use combinatorial dual indexes for demultiplexing.
        output_dir (str): Directory to save the output demultiplexed FASTQ files.
        error_rate (float | None): Maximum expected error rate (default: 0.14).
        min_overlap (int | None): Minimum overlap length for adapter matching (default: 3).
    """
    error_rate_param = error_rate if error_rate is not None else "0.14"
    min_overlap_param = min_overlap if min_overlap is not None else "3"

    if combinatorial:
        command = (
            f"cutadapt -e {error_rate_param} -O {min_overlap_param} --no-indels --cores=0 "
            f"--revcomp "
            f"-g ^file:{forward_fasta} "
            f"-G ^file:{reverse_fasta} "
            f"-o '{output_dir}/demux-{{name1}}-{{name2}}.1.fastq.gz' "
            f"-p '{output_dir}/demux-{{name1}}-{{name2}}.2.fastq.gz' "
            f"{fq_gz_1} "
            f"{fq_gz_2} "
        )
    else:
        command = (
            f"cutadapt -e {error_rate_param} -O {min_overlap_param} --no-indels --pair-adapters --cores=0 "
            f"--revcomp "
            f"-g ^file:{forward_fasta} "
            f"-G ^file:{reverse_fasta} "
            f"-o '{output_dir}/demux-{{name}}.1.fastq.gz' "
            f"-p '{output_dir}/demux-{{name}}.2.fastq.gz' "
            f"{fq_gz_1} "
            f"{fq_gz_2} "
        )

    run_command(command, output_dir)


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description=(
            """
            Demultiplex with cutadapt paired end FASTQ files using forward and
            reverse FASTA files containing barcodes. You have the option
            between the default mode where paired adapters with unique dual
            indices are assumed and the mode combinatorial dual indexes for
            demultiplexing.
            """
        )
    )
    _ = parser.add_argument(
        "fq_gz_1", type=str, help="Path to the first FASTQ file (R1)"
    )
    _ = parser.add_argument(
        "fq_gz_2", type=str, help="Path to the second FASTQ file (R2)"
    )
    _ = parser.add_argument(
        "forward_fasta",
        type=str,
        help="Path to the forward FASTA file containing barcodes",
    )
    _ = parser.add_argument(
        "reverse_fasta",
        type=str,
        help="Path to the reverse FASTA file containing barcodes",
    )

    _ = parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="Directory to save the output demultiplexed FASTQ files (default: ./)",
    )

    _ = parser.add_argument(
        "-c",
        "--combinatorial",
        action="store_true",
        help="""
        Use combinatorial dual indexes for demultiplexing paired-end reads
        (default: False). In the default case demultiplexing unique dual
        indices is executed.
        """,
        default=False,
    )

    _ = parser.add_argument(
        "-e",
        "--error-rate",
        type=float,
        help="Maximum expected error rate (default: 0.14)",
    )

    _ = parser.add_argument(
        "--min-overlap",
        type=int,
        help="Minimum overlap length for adapter matching (default: 3)",
    )

    args = parser.parse_args()

    run_cutadapt(
        args.forward_fasta,
        args.reverse_fasta,
        args.fq_gz_1,
        args.fq_gz_2,
        args.combinatorial,
        args.output,
        args.error_rate,
        args.min_overlap,
    )


if __name__ == "__main__":
    main()
