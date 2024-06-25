import os
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Generate a sample sheet from filenames originating from demultiplex cutadapt script in a directory"
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The directory containing the files. Files are expected to have this format: demux-{sample_name}_R{1,2}.fastq.gz",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Directory {args.directory} does not exist.")
        return

    filenames = os.listdir(args.directory)
    for filename in filenames:
        print(filename)


if __name__ == "__main__":
    main()
