import argparse
import io
import multiprocessing
from pathlib import Path

import pandas as pd

from command_utils import run_command
from file_utils import parse_input_path, write_output


def count_reads(file_paths: list[Path], cpu_count: int) -> tuple[pd.DataFrame, str]:
    """
    Count reads in FASTA/FASTQ files using seqkit stats.

    Args:
        file_paths (list[Path]): List of file paths to process
        cpu_count (int): Number of CPUs to use for processing

    Returns:
        tuple[pd.DataFrame, str]: A tuple containing:
            - DataFrame containing the file and num_seqs columns from seqkit stats output
            - Raw command output as a string
    """
    file_paths_str = " ".join(str(path) for path in file_paths)
    command = f"seqkit stats {file_paths_str} -T --quiet -j {cpu_count}"

    output = run_command(command)

    df = pd.read_csv(io.StringIO(output), sep="\t")
    df = df[["file", "num_seqs"]]
    return df, output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Count reads in a directory of input FASTA/FASTQ files using seqkit stats. "
        "The results are printed to stdout. If an output path is specified, "
        "the results are stored as 'read_counts.tsv' in the specified output path. "
        "The raw seqkit stats output is saved as 'seqkit_stats.tsv' in both the input "
        "directory and the output directory (if specified). "
        "Use -h or --help to show this help message and exit."
    )
    _ = parser.add_argument(
        "input_path",
        help="Path to the directory containing FASTA/FASTQ files",
        type=Path,
    )
    _ = parser.add_argument(
        "-o",
        "--output",
        help="Output directory path. If not specified, only stdout output is produced.",
        type=Path,
    )

    args = parser.parse_args()

    try:
        file_paths = parse_input_path(args.input_path)
        read_counts, raw_output = count_reads(file_paths, multiprocessing.cpu_count())

        write_output(raw_output, "seqkit_stats.tsv", args.input_path)
        if args.output:
            args.output.mkdir(parents=True, exist_ok=True)
            write_output(
                read_counts.to_csv(sep="\t", index=False, lineterminator="\n"),
                "read_counts.tsv",
                args.output,
            )
            write_output(raw_output, "seqkit_stats.tsv", args.output)
        
        print(read_counts.to_string(index=False))

    except (ValueError, RuntimeError) as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
