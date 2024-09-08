import argparse
import os
import re
import subprocess

import pandas as pd


def parse_input_path(input_path: str) -> set[str]:
    """
    Parse files in the input path, extract their file endings, and ensure they are paired-end.

    Args:
        input_path (str): Path to the directory containing FASTA/FASTQ files

    Returns:
        set[str]: Set of file endings found

    Raises:
        ValueError: If no valid files are found, file endings are not identical, not in accepted formats, or not paired-end
    """
    accepted_endings = {"fasta", "fastq", "fq", "fa", "fna"}
    file_list: set[str] = set()
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
                base_name, read_number, ending, _ = match.groups()
                ending = ending.lower()
                if ending in accepted_endings:
                    file_list.add(file_path)
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

    return endings


def count_reads(input_path: str, file_endings: set[str]) -> pd.DataFrame:
    """
    Count reads in FASTA/FASTQ files using seqkit stats.

    Args:
        input_path (str): Path to the directory containing FASTA/FASTQ files
        file_endings (set[str]): Set of file endings found in the input path

    Returns:
        pd.DataFrame: DataFrame containing the seqkit stats output
    """
    ending = next(iter(file_endings))
    command = f"seqkit stats {input_path}/*{{1,2}}.{ending} -T --quiet"

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        df = pd.read_csv(pd.compat.StringIO(result.stdout), sep="\t")
        return df
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running seqkit stats: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Count reads in FASTA/FASTQ files and subset reads with specific adapter or primer sequences using seqkit."
    )
    _ = parser.add_argument(
        "input_path", help="Path to the directory containing FASTA/FASTQ files"
    )
    _ = parser.add_argument(
        "forward_barcode", help="Path to the forward barcode FASTA file"
    )
    _ = parser.add_argument(
        "reverse_barcode", help="Path to the reverse barcode FASTA file"
    )
    _ = parser.add_argument(
        "forward_primer", help="Path to the forward primer FASTA file"
    )
    _ = parser.add_argument(
        "reverse_primer", help="Path to the reverse primer FASTA file"
    )
    _ = parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output TSV file path. If not specified, output will be printed to stdout.",
    )

    args = parser.parse_args()

    try:
        file_endings = parse_input_path(args.input_path)
        read_counts = count_reads(args.input_path, file_endings)

        if args.output:
            read_counts.to_csv(args.output, sep="\t", index=False)
        else:
            print(read_counts.to_string(index=False))
    except (ValueError, RuntimeError) as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
