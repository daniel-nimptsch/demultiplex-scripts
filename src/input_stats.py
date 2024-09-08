import argparse
import io
import os
import re
import subprocess

import pandas as pd

BARCODE_PATH = ""
PRIMER_PATH = ""


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
    Count reads in FASTA/FASTQ files using seqkit stats.

    Args:
        file_paths (list[str]): List of file paths to process

    Returns:
        pd.DataFrame: DataFrame containing the file and num_seqs columns from seqkit stats output
    """
    file_paths_str = " ".join(file_paths)
    command = f"seqkit stats {file_paths_str} -T --quiet -j 8"

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        df = pd.read_csv(io.StringIO(result.stdout), sep="\t")
        df = df[["file", "num_seqs"]]
        return df
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running seqkit stats: {e}")


def count_motifs(file_paths: list[str]) -> pd.DataFrame:
    """
    Count motifs in the input files using seqkit grep.

    Args:
        file_paths (list[str]): List of file paths to process

    Returns:
        pd.DataFrame: DataFrame with columns for file paths and motif counts
    """
    df = pd.DataFrame({"file": file_paths})

    # Get all pattern names from barcode and primer files
    barcode_patterns = set(run_command(f"seqkit seq -n {BARCODE_PATH}"))
    primer_patterns = set(run_command(f"seqkit seq -n {PRIMER_PATH}"))
    all_patterns = barcode_patterns.union(primer_patterns)

    # Initialize columns for all patterns with 0
    for pattern in all_patterns:
        df[pattern] = 0

    for fasta in file_paths:
        barcode_command = f"seqkit locate -t {fasta} -M -m 1 -f {BARCODE_PATH}"
        primer_command = f"seqkit locate -t {fasta} -dM -f {PRIMER_PATH}"

        barcode_counts = parse_seqkit_output(run_command(barcode_command))
        primer_counts = parse_seqkit_output(run_command(primer_command))

        for pattern, count in {**barcode_counts, **primer_counts}.items():
            df.loc[df['file'] == fasta, pattern] = count

    return df

def parse_seqkit_output(output: list[str]) -> dict[str, int]:
    """
    Parse the output of seqkit locate command.

    Args:
        output (list[str]): List of output lines from seqkit locate

    Returns:
        dict[str, int]: Dictionary with pattern names as keys and their counts as values
    """
    pattern_counts = {}
    for line in output[1:]:  # Skip the header line
        columns = line.split('\t')
        if len(columns) >= 2:
            pattern = columns[1]
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    return pattern_counts


def run_command(command: str) -> list[str]:
    result = subprocess.run(
        command, shell=True, check=True, capture_output=True, text=True
    )
    return result.stdout.strip().split("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Count reads in FASTA/FASTQ files and subset reads with specific adapter or primer sequences using seqkit."
    )
    _ = parser.add_argument(
        "input_path", help="Path to the directory containing FASTA/FASTQ files"
    )
    _ = parser.add_argument("barcode", help="Path to the barcode FASTA file")
    _ = parser.add_argument("primer", help="Path to the primer FASTA file")
    _ = parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output TSV file path. If not specified, output will be printed to stdout.",
    )

    args = parser.parse_args()

    global BARCODE_PATH, PRIMER_PATH
    BARCODE_PATH = args.barcode
    PRIMER_PATH = args.primer

    try:
        file_paths = parse_input_path(args.input_path)
        read_counts = count_reads(file_paths)
        motif_counts = count_motifs(file_paths)

        result = pd.merge(read_counts, motif_counts, on="file")

        if args.output:
            result.to_csv(args.output, sep="\t", index=False)
        else:
            print(result.to_string(index=False))

    except (ValueError, RuntimeError) as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
