import argparse
import io
import os
import re
import subprocess

import pandas as pd
from Bio import SeqIO


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
    command = f"seqkit stats {file_paths_str} -T --quiet"

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        df = pd.read_csv(io.StringIO(result.stdout), sep="\t")
        # Keep only the 'file' and 'num_seqs' columns
        df = df[["file", "num_seqs"]]
        return df
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running seqkit stats: {e}")


# Global variables for barcode and primer FASTA paths
FORWARD_BARCODE_PATH = ""
REVERSE_BARCODE_PATH = ""
FORWARD_PRIMER_PATH = ""
REVERSE_PRIMER_PATH = ""


def get_motifs() -> dict:
    """
    Read all barcode and primer FASTA files and store the sequence names and sequences as a dictionary.

    Returns:
        dict: A dictionary containing sequence names as keys and sequences as values.
    """
    motif_files = {
        FORWARD_BARCODE_PATH,
        REVERSE_BARCODE_PATH,
        FORWARD_PRIMER_PATH,
        REVERSE_PRIMER_PATH,
    }

    motifs = {}
    for file_path in motif_files:
        with open(file_path, "r") as handle:
            for record in SeqIO.parse(handle, "fasta"):
                motifs[record.id] = str(record.seq)

    return motifs


def count_motifs(file_paths: list[str]) -> pd.DataFrame:
    """
    Count motifs in the input files using seqkit grep.

    Args:
        file_paths (list[str]): List of file paths to process

    Returns:
        pd.DataFrame: DataFrame with columns for file paths and motif counts
    """
    motifs = get_motifs()

    df = pd.DataFrame({"file": file_paths})

    for motif_name, motif_seq in motifs.items():
        counts = []
        for fasta in file_paths:
            command = f"seqkit grep {fasta} -i -s -p {motif_seq} -C -j $(nproc)"
            print(command)
            try:
                result = subprocess.run(
                    command, shell=True, check=True, capture_output=True, text=True
                )
                output_lines = result.stdout.strip().split("\n")
                print(output_lines)
                if int(output_lines[0]):
                    count = int(output_lines[0])
                else:
                    print(
                        f"Warning: Unexpected output format for motif {motif_name} in file {fasta}"
                    )
                    count = pd.NA
            except subprocess.CalledProcessError as e:
                print(
                    f"Error running seqkit grep for motif {motif_name} in file {fasta}: {e}"
                )
                count = 0
            except ValueError as e:
                print(
                    f"Error parsing seqkit grep output for motif {motif_name} in file {fasta}: {e}"
                )
                count = 0
            counts.append(count)
        df[motif_name] = counts

    return df


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

    # Set global variables for barcode and primer FASTA paths
    global FORWARD_BARCODE_PATH, REVERSE_BARCODE_PATH, FORWARD_PRIMER_PATH, REVERSE_PRIMER_PATH
    FORWARD_BARCODE_PATH = args.forward_barcode
    REVERSE_BARCODE_PATH = args.reverse_barcode
    FORWARD_PRIMER_PATH = args.forward_primer
    REVERSE_PRIMER_PATH = args.reverse_primer

    try:
        file_paths = parse_input_path(args.input_path)
        read_counts = count_reads(file_paths)
        motif_counts = count_motifs(file_paths)

        # Merge read_counts and motif_counts DataFrames
        result = pd.merge(read_counts, motif_counts, on="file")

        if args.output:
            result.to_csv(args.output, sep="\t", index=False)
        else:
            print(result.to_string(index=False))

    except (ValueError, RuntimeError) as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
