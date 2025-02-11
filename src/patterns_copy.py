import argparse
import sys
from pathlib import Path
import shutil


def rename_files(patterns, output_path):
    for pattern in patterns:
        old_name, new_name = pattern.strip().split()
        old_path = Path(old_name)
        new_path = output_path / new_name
        if old_path.exists():
            try:
                shutil.copy(old_path, new_path)
            except Exception as e:
                print(f"Error copying {old_path} to {new_path}: {e}")
        else:
            print(f"File {old_path} does not exist")


def main():
    parser = argparse.ArgumentParser(
        description="""
        Rename files based on patterns provided either as an argument or from
        stdin. The patterns should be a piar of words separated by space with
        each line of the file being one pair. The first name should match a
        filepath and the second is the filepath that the file will be copied
        to.
        """
    )
    parser.add_argument(
        "patterns",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Path to the patterns file (default: stdin)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="""
            The output dir to copy the renamed. If not provided, output
            will be ./.
            """,
    )

    args = parser.parse_args()

    patterns = args.patterns.readlines()
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    rename_files(patterns, output_path)
    args.patterns.close()


if __name__ == "__main__":
    main()
