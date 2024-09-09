import io
from pathlib import Path

import pandas as pd

from file_utils import run_command


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
