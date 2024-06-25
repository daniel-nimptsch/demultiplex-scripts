import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate a sample sheet from filenames in a directory.")
    parser.add_argument("directory", type=str, help="The directory containing the files.")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Directory {args.directory} does not exist.")
        return

    filenames = os.listdir(args.directory)
    for filename in filenames:
        print(filename)

if __name__ == "__main__":
    main()
