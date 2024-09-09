import argparse
import io
import multiprocessing
import os
import re
import subprocess
from dataclasses import dataclass

import pandas as pd


@dataclass
class Config:
    barcode_path: str
    primer_path: str
    verbose: bool
    cpu_count: int = multiprocessing.cpu_count()


# Global configuration object
config: Config


def parse_input_path(input_path: str) -> list[str]:
    """
    Parse files in the input path, ensure they are paired-end, and return their file paths.

    Args:
        input_path (str): Path to the directory containing FASTA/FASTQ files

    Returns:
        list[str]: List of file paths for valid paired-end FASTA/FASTQ files

    Raises:
        ValueError: If no valid files are found, file endings are not identical, not in accepted formats, or not paired-end
    """
    accepted_endings = {"fasta", "fastq", "fq", "fa", "fna"}
    file_list: list[str] = []
    endings: set[str] = set()
    paired_files: dict[str, list[str]] = {}

    for file in os.listdir(input_path):
        file_path = os.path.join(input_path, file)
        if os.path.isfile(file_path):
            # Regex for paired-end files: base_name + 1 or 2 + .extension + optional .gz
            # Example: sample_R1.fastq.gz or sample_2.fq
            paired_end_pattern = r"^(.+)([12])\.([^.]+)(\.gz)?$"
            match = re.match(paired_end_pattern, file)
            if match:
                base_name, read_number, ending, gz = match.groups()
                ending = ending.lower()
                if ending in accepted_endings:
                    file_list.append(file_path)
                    if gz:
                        endings.add(f"{ending}.gz")
                    else:
                        endings.add(ending)
                    if base_name not in paired_files:
                        paired_files[base_name] = []
                    paired_files[base_name].append(read_number)

    if not file_list:
        raise ValueError(f"No valid FASTA/FASTQ files found in {input_path}")

    if len(endings) > 1:
        raise ValueError(
            f"Multiple file endings found: {', '.join(endings)}. All files should have the same ending."
        )

    incomplete_pairs = [base for base, reads in paired_files.items() if len(reads) != 2]
    if incomplete_pairs:
        raise ValueError(
            f"Incomplete paired-end files found for: {', '.join(incomplete_pairs)}"
        )

    return file_list


def count_reads(file_paths: list[str]) -> pd.DataFrame:
    """
    Count reads and get average sequence length in FASTA/FASTQ files using seqkit stats.

    Args:
        file_paths (list[str]): List of file paths to process

    Returns:
        pd.DataFrame: DataFrame containing the file, num_seqs, and avg_len columns from seqkit stats output
    """
    file_paths_str = " ".join(file_paths)
    command = f"seqkit stats {file_paths_str} -T --quiet -j {config.cpu_count}"

    output = run_command(command)

    # Write the raw result to a file
    with open("seqkit_stats_raw.tsv", "w") as f:
        _ = f.write(output)

    df = pd.read_csv(io.StringIO(output), sep="\t")
    df = df[["file", "num_seqs", "avg_len"]]

    return df


def get_patterns() -> tuple[dict[str, str], dict[str, str]]:
    barcode_command = f"seqkit seq -n -s {config.barcode_path} -j {config.cpu_count}"
    primer_command = f"seqkit seq -n -s {config.primer_path} -j {config.cpu_count}"

    barcode_output = run_command(barcode_command).splitlines()
    primer_output = run_command(primer_command).splitlines()

    barcode_patterns = {line.split()[0]: line.split()[1] for line in barcode_output}
    primer_patterns = {line.split()[0]: line.split()[1] for line in primer_output}
    return barcode_patterns, primer_patterns


def empty_pattern_df(patterns: dict[str, str], file_paths: list[str]) -> pd.DataFrame:
    df = pd.DataFrame({"file": file_paths})
    for pattern in patterns.keys():
        df[pattern] = 0
    return df


def count_motifs(file_paths: list[str]) -> pd.DataFrame:
    """
    Count motifs in the input files using seqkit locate for both barcodes and primers.

    Args:
        file_paths (list[str]): List of file paths to process

    Returns:
        pd.DataFrame: DataFrame with rows for file paths and columns for motif counts
    """

    barcode_patterns, primer_patterns = get_patterns()
    all_patterns = {**barcode_patterns, **primer_patterns}
    df = empty_pattern_df(all_patterns, file_paths)

    for fasta in file_paths:
        # -d allow degenerate bases, -i case insensitive
        barcode_patterns_str = ",".join(f"^{seq}" for seq in barcode_patterns.values())
        primer_patterns_str = ",".join(f"^{seq}" for seq in primer_patterns.values())
        
        barcode_command = (
            f"seqkit locate {fasta} -di -p {barcode_patterns_str} -j {config.cpu_count}"
        )
        primer_command = (
            f"seqkit locate {fasta} -di -p {primer_patterns_str} -j {config.cpu_count}"
        )

        barcode_output = run_command(barcode_command)
        primer_output = run_command(primer_command)

        # Write raw outputs to files
        with open("barcode_locate.tsv", "w") as f:
            _ = f.write(barcode_output)
        with open("primer_locate.tsv", "w") as f:
            _ = f.write(primer_output)

        barcode_counts = parse_seqkit_locate(barcode_output.strip().split("\n"), barcode_patterns)
        primer_counts = parse_seqkit_locate(primer_output.strip().split("\n"), primer_patterns)

        for pattern, count in {**barcode_counts, **primer_counts}.items():
            df.loc[df["file"] == fasta, pattern] = count

    return df


def parse_seqkit_locate(output: list[str], patterns: dict[str, str]) -> dict[str, int]:
    """
    Parse the output of seqkit locate command.

    Args:
        output (list[str]): List of output lines from seqkit locate
        patterns (dict[str, str]): Dictionary of pattern names and their sequences

    Returns:
        dict[str, int]: Dictionary with pattern names as keys and their counts as values
    """
    pattern_counts = {name: 0 for name in patterns.keys()}
    seq_to_name = {seq: name for name, seq in patterns.items()}
    
    for line in output[1:]:
        columns = line.split("\t")
        if len(columns) >= 5:
            seq = columns[1]
            if seq in seq_to_name:
                pattern_name = seq_to_name[seq]
                pattern_counts[pattern_name] += 1
    return pattern_counts


def run_command(command: str) -> str:
    """
    Execute a shell command and return its output as a list of strings.

    Args:
        command (str): The shell command to execute.

    Returns:
        str: The command's output split into lines.

    Raises:
        subprocess.CalledProcessError: If the command execution fails.
    """
    try:
        if config.verbose:
            print(command)
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running seqkit stats: {e}")
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Count reads in input FASTA/FASTQ files and the subset of reads with a specific adapter or primer sequences."
    )
    _ = parser.add_argument(
        "input_path",
        help="Path to the directory containing FASTA/FASTQ files",
        type=str,
    )
    _ = parser.add_argument("barcode", help="Path to the barcode FASTA file", type=str)
    _ = parser.add_argument("primer", help="Path to the primer FASTA file", type=str)
    _ = parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output TSV file path. If not specified, output will be printed to stdout.",
        type=str,
    )
    _ = parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print seqkit commands and their outputs",
    )

    args = parser.parse_args()
    input_path = str(args.input_path)
    output = str(args.output)

    global config
    config = Config(
        barcode_path=args.barcode, primer_path=args.primer, verbose=args.verbose
    )

    try:
        file_paths = parse_input_path(input_path)
        read_counts = count_reads(file_paths)
        motif_counts = count_motifs(file_paths)
        result = pd.merge(read_counts, motif_counts, on="file")

        if output:
            result.to_csv(output, sep="\t", index=False)
        else:
            print(result.to_string(index=False))

    except (ValueError, RuntimeError) as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
