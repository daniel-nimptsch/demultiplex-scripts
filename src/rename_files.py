import argparse
import sys
import os

def rename_files(patterns):
    for pattern in patterns:
        old_name, new_name = pattern.strip().split()
        if os.path.exists(old_name):
            os.rename(old_name, new_name)
            print(f"Renamed {old_name} to {new_name}")
        else:
            print(f"File {old_name} does not exist")

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

    if args.patterns == sys.stdin:
        print("Reading patterns from stdin...")
    patterns = args.patterns.readlines()
    rename_files(patterns)

if __name__ == "__main__":
    main()
