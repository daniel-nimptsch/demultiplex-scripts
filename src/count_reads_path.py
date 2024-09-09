import io
from pathlib import Path

import pandas as pd

from command_utils import run_command


def count_reads(file_paths: list[Path], cpu_count: int) -> pd.DataFrame:
    """
    Count reads in FASTA/FASTQ files using seqkit stats.

    Args:
        file_paths (list[Path]): List of file paths to process
        cpu_count (int): Number of CPUs to use for processing

    Returns:
        pd.DataFrame: DataFrame containing the file and num_seqs columns from seqkit stats output
    """
    file_paths_str = " ".join(str(path) for path in file_paths)
    command = f"seqkit stats {file_paths_str} -T --quiet -j {cpu_count}"

    output = run_command(command)

    df = pd.read_csv(io.StringIO(output), sep="\t")
    df = df[["file", "num_seqs"]]
    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Count reads in a dir of input FASTA/FASTQ files."
    )
    _ = parser.add_argument(
        "input_path",
        help="Path to the directory containing FASTA/FASTQ files",
        type=Path,
    )
    _ = parser.add_argument(
        "-o",
        "--output",
        default=Path("./"),
        help="Output directory path. Default is current directory.",
        type=Path,
    )

    try:
        file_paths = parse_input_path(args.input_path)
        read_counts = count_reads(file_paths, multiprocessing.cpu_count())
        write_output(
            read_counts.to_csv(sep="\t", index=False),
            "seqkit_stats.tsv",
            args.output_path,
        )
        print(read_counts.to_string(index=False))

    except (ValueError, RuntimeError) as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
