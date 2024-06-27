import argparse
import sys
from pathlib import Path
import shutil


def rename_files(patterns, output_path):
    for pattern in patterns:
        old_name, new_name = pattern.strip().split()
        old_path = Path(old_name)
        new_path = output_path + Path(new_name)
        if old_path.exists():
            shutil.copy(old_path, new_path)
        else:
            print(f"File {old_path} does not exist")


def main():
    parser = argparse.ArgumentParser(
        description="Rename files based on patterns provided either as an argument or from stdin."
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
    rename_files(patterns, output_path)


if __name__ == "__main__":
    main()
