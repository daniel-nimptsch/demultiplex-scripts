import argparse
import sys
from pathlib import Path


def rename_files(patterns):
    for pattern in patterns:
        old_name, new_name = pattern.strip().split()
        old_path = Path(old_name)
        new_path = Path(new_name)
        if old_path.exists():
            old_path.rename(new_path)
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

    args = parser.parse_args()

    patterns = args.patterns.readlines()
    rename_files(patterns)


if __name__ == "__main__":
    main()
