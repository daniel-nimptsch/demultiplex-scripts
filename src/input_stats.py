import argparse
import os
import re
import subprocess

import pandas as pd


def parse_input_path(input_path: str) -> set[str]:
    """
    Parse files in the input path, extract their file endings, and check if they are paired-end.

    Args:
        input_path (str): Path to the directory containing FASTA/FASTQ files

    Returns:
        tuple[set[str], bool]: A tuple containing:
            - Set of file endings found
            - Boolean indicating if the files are paired-end

    Raises:
        ValueError: If file endings are not identical or not in accepted formats
    """
    accepted_endings = {"fasta", "fastq", "fq", "fa", "fna"}
    file_list: set[str] = set()
    endings: set[str] = set()
    paired_files: set[str] = set()
    unpaired_files: set[str] = set()

    for file in os.listdir(input_path):
        file_path = os.path.join(input_path, file)
        if os.path.isfile(file_path):
            match = re.match(r"^(.+)([12])\.([^.]+)(\.gz)?$", file)
            if match:
                base_name, pair_num, ending, _ = match.groups()
                ending = ending.lower()
                if ending in accepted_endings:
                    file_list.add(file_path)
                    endings.add(ending)
                    paired_files.add(base_name)
            else:
                match = re.match(r"^(.+)\.([^.]+)(\.gz)?$", file)
                if match:
                    base_name, ending, _ = match.groups()
                    ending = ending.lower()
                    if ending in accepted_endings:
                        file_list.add(file_path)
                        endings.add(ending)
                        unpaired_files.add(base_name)

    if not file_list:
        raise ValueError(f"No valid FASTA/FASTQ files found in {input_path}")

    if len(endings) > 1:
        raise ValueError(
            f"Multiple file endings found: {', '.join(endings)}. All files should have the same ending."
        )

    is_paired_end = len(paired_files) > 0 and len(unpaired_files) == 0

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
    command = f"seqkit stats {input_path}/*{1,2}*.{ending} -T --quiet"

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
