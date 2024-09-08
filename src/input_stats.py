import argparse
import os
import re
from typing import list, tuple


def get_input_files(input_path: str) -> list[tuple[str, str]]:
    """
    List files in the input path and extract their file endings.

    Args:
        input_path (str): Path to the directory containing FASTA/FASTQ files

    Returns:
        List[Tuple[str, str]]: List of tuples containing (file_path, file_ending)

    Raises:
        ValueError: If file endings are not identical or not in accepted formats
    """
    accepted_endings = {"fasta", "fastq", "fq", "fa", "fna"}
    file_list = []
    endings = set()

    for file in os.listdir(input_path):
        file_path = os.path.join(input_path, file)
        if os.path.isfile(file_path):
            match = re.match(r"^.+\.([^.]+)(\.gz)?$", file)
            if match:
                ending = match.group(1).lower()
                if ending in accepted_endings:
                    file_list.append((file_path, ending))
                    endings.add(ending)

    if not file_list:
        raise ValueError(f"No valid FASTA/FASTQ files found in {input_path}")

    if len(endings) > 1:
        raise ValueError(
            f"Multiple file endings found: {', '.join(endings)}. All files should have the same ending."
        )

    return file_list


def main():
    parser = argparse.ArgumentParser(
        description="Count reads in FASTA/FASTQ files and subset reads with specific adapter or primer sequences using seqkit."
    )
    _ = parser.add_argument(
        "input_path", help="Path to the directory containing FASTA/FASTQ files"
    )
    _ = parser.add_argument(
        "--forward_barcode", help="Path to the forward barcode FASTA file"
    )
    _ = parser.add_argument(
        "--reverse_barcode", help="Path to the reverse barcode FASTA file"
    )
    _ = parser.add_argument(
        "--forward_primer", help="Path to the forward primer FASTA file"
    )
    _ = parser.add_argument(
        "--reverse_primer", help="Path to the reverse primer FASTA file"
    )
    _ = parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output TSV file path. If not specified, output will be printed to stdout.",
    )

    args = parser.parse_args()

    try:
        input_files = get_input_files(args.input_path)
        print(f"Found {len(input_files)} valid input files.")
        # TODO: Implement the logic for counting reads and generating the output TSV
    except ValueError as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
