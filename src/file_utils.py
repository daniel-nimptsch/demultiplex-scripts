import re
from pathlib import Path


def parse_input_path(input_path: Path) -> list[Path]:
    """
    Parse files in the input path, ensure they are paired-end, and return their
    file paths.

    Args:
        input_path (Path): Path to the directory containing FASTA/FASTQ files

    Returns:
        list[Path]: List of Path objects for valid paired-end FASTA/FASTQ files

    Raises:
        ValueError: If no valid files are found, file endings are not
        identical, not in accepted formats, or not paired-end
    """
    accepted_endings = {"fasta", "fastq", "fq", "fa", "fna"}
    file_list: list[Path] = []
    endings: set[str] = set()
    paired_files: dict[str, list[str]] = {}

    for file in input_path.iterdir():
        if file.is_file():
            # Regex for paired-end files: base_name + 1 or 2 + .extension + optional .gz
            # Example: sample_R1.fastq.gz or sample_2.fq
            paired_end_pattern = r"^(.+)([12])\.([^.]+)(\.gz)?$"
            match = re.match(paired_end_pattern, file.name)
            if match:
                base_name, read_number, ending, gz = match.groups()
                ending = ending.lower()
                if ending in accepted_endings:
                    file_list.append(file)
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


def write_output(output: str, filename: str, output_path: Path) -> None:
    """
    Write the given output to a file in the specified output path.

    Args:
        output (str): The content to write to the file.
        filename (str): The name of the file to create.
        output_path (Path): The directory path where the file should be
        created.
    """
    with open(output_path / filename, "w") as f:
        _ = f.write(output)
