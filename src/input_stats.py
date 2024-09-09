import argparse
import multiprocessing
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from command_utils import run_command
from file_utils import parse_input_path, write_output


@dataclass
class Config:
    barcode_path: Path
    primer_path: Path
    verbose: bool
    output_path: Path
    write_to_file: bool
    cpu_count: int = multiprocessing.cpu_count()


config: Config


def read_input_table(file_path: Path | None) -> pd.DataFrame:
    """
    Read the input table from a file or stdin.

    Args:
        file_path (Path | None): Path to the input file, or None if reading from stdin

    Returns:
        pd.DataFrame: DataFrame containing the input table
    """
    if file_path is None:
        return pd.read_csv(sys.stdin, sep="\t")
    else:
        return pd.read_csv(file_path, sep="\t")


def get_patterns() -> tuple[dict[str, str], dict[str, str]]:
    """
    Retrieve barcode and primer patterns from the specified files.

    Returns:
        tuple[dict[str, str], dict[str, str]]: A tuple containing two dictionaries:
            1. Barcode patterns (key: name, value: sequence)
            2. Primer patterns (key: name, value: sequence)
    """

    def get_pattern_dict(
        file_path: Path, cpu_count: int, verbose: bool
    ) -> dict[str, str]:
        name_command = f"seqkit seq -n {file_path} -j {cpu_count}"
        seq_command = f"seqkit seq -s {file_path} -j {cpu_count}"
        names = run_command(name_command, verbose).splitlines()
        seqs = run_command(seq_command, verbose).splitlines()
        return dict(zip(names, seqs))

    barcode_patterns = get_pattern_dict(
        config.barcode_path, config.cpu_count, config.verbose
    )
    primer_patterns = get_pattern_dict(
        config.primer_path, config.cpu_count, config.verbose
    )
    return barcode_patterns, primer_patterns


def empty_pattern_df(patterns: dict[str, str], file_paths: list[Path]) -> pd.DataFrame:
    df = pd.DataFrame({"file": [str(path) for path in file_paths]})
    for pattern in patterns.keys():
        df[pattern] = 0
    return df


def run_seqkit_locate(fasta: Path, patterns: dict[str, str], is_primer: bool) -> str:
    if is_primer:
        command = (
            f"seqkit locate {fasta} -di -f {config.primer_path} -j {config.cpu_count}"
        )
    else:
        patterns_str = ",".join(f"^{seq}" for seq in patterns.values())
        command = f"seqkit locate {fasta} -di -p {patterns_str} -j {config.cpu_count}"
    return run_command(command, config.verbose)


def parse_seqkit_locate(
    output: list[str], patterns: dict[str, str], use_pattern_names: bool = False
) -> dict[str, int]:
    """
    Parse the output of seqkit locate command.

    Args:
        output (list[str]): List of output lines from seqkit locate
        patterns (dict[str, str]): Dictionary of pattern names and their sequences
        use_pattern_names (bool): If True, search for pattern names instead of sequences (for -f flag)

    Returns:
        dict[str, int]: Dictionary with pattern names as keys and their counts as values
    """
    pattern_counts = {name: 0 for name in patterns}

    if use_pattern_names:
        search_dict = {name: name for name in patterns}
    else:
        search_dict = {seq.lstrip("^"): name for name, seq in patterns.items()}

    for line in output[1:]:
        try:
            _, pattern, *_ = line.split("\t")
            pattern = pattern.lstrip("^") if not use_pattern_names else pattern
            if pattern in search_dict:
                pattern_name = search_dict[pattern]
                pattern_counts[pattern_name] += 1
        except ValueError:
            continue

    return pattern_counts


def count_motifs(file_paths: list[Path]) -> pd.DataFrame:
    """
    Count motifs in the input files using seqkit locate for both barcodes and primers.

    Args:
        file_paths (list[Path]): List of file paths to process

    Returns:
        pd.DataFrame: DataFrame with rows for file paths and columns for motif counts
    """
    barcode_patterns, primer_patterns = get_patterns()
    all_patterns = {**barcode_patterns, **primer_patterns}
    df = empty_pattern_df(all_patterns, file_paths)

    for fasta in file_paths:
        fasta_name = fasta.stem
        barcode_output = run_seqkit_locate(fasta, barcode_patterns, is_primer=False)
        primer_output = run_seqkit_locate(fasta, primer_patterns, is_primer=True)

        write_output(
            barcode_output, f"{fasta_name}_barcode_stats.tsv", config.output_path
        )
        write_output(
            primer_output, f"{fasta_name}_primer_stats.tsv", config.output_path
        )

        barcode_counts = parse_seqkit_locate(
            barcode_output.strip().split("\n"),
            barcode_patterns,
            use_pattern_names=False,
        )
        primer_counts = parse_seqkit_locate(
            primer_output.strip().split("\n"), primer_patterns, use_pattern_names=True
        )

        for pattern, count in {**barcode_counts, **primer_counts}.items():
            df.loc[df["file"] == str(fasta), pattern] = count

    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Count subset of reads with specific adapter or primer sequences in input FASTA/FASTQ files."
    )
    _ = parser.add_argument(
        "input_table",
        nargs="?",
        type=Path,
        help="Path to the input table file with fastq read counts. If not provided, reads from stdin.",
    )
    _ = parser.add_argument("barcode", help="Path to the barcode FASTA file", type=Path)
    _ = parser.add_argument("primer", help="Path to the primer FASTA file", type=Path)
    _ = parser.add_argument(
        "-o",
        "--output",
        default=Path("./"),
        help="Output directory path. Default is current directory.",
        type=Path,
    )
    _ = parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print seqkit commands and their outputs",
    )
    _ = parser.add_argument(
        "-w",
        "--write-to-file",
        action="store_true",
        default=False,
        help="Write result to a TSV file. Default is False.",
    )

    args = parser.parse_args()
    output_path = args.output
    output_path.mkdir(parents=True, exist_ok=True)

    global config
    config = Config(
        barcode_path=args.barcode,
        primer_path=args.primer,
        verbose=args.verbose,
        output_path=output_path,
        write_to_file=args.write_to_file,
    )

    try:
        read_counts = read_input_table(args.input_table)
        file_paths = [Path(file) for file in read_counts["file"]]
        motif_counts = count_motifs(file_paths)
        result = pd.merge(read_counts, motif_counts, on="file")

        if config.write_to_file:
            result.to_csv(
                config.output_path / "motif_counts.tsv", sep="\t", index=False
            )
            print(f"Results written to {config.output_path / 'motif_counts.tsv'}")
        else:
            print(result.to_string(index=False))

    except (ValueError, RuntimeError) as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
