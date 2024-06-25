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
    sample_dict = {}
    for filename in filenames:
        if filename.startswith("demux-") and filename.endswith(".fastq.gz"):
            sample_name = filename.split("_R")[0].replace("demux-", "")
            if sample_name.lower() != "unknown":
                if sample_name not in sample_dict:
                    sample_dict[sample_name] = {"R1": None, "R2": None}
                if "_R1" in filename:
                    sample_dict[sample_name]["R1"] = os.path.join(args.directory, filename)
                elif "_R2" in filename:
                    sample_dict[sample_name]["R2"] = os.path.join(args.directory, filename)
    
    for sample_name, paths in sample_dict.items():
        if paths["R1"] and paths["R2"]:
            print(f"{sample_name},{paths['R1']},{paths['R2']}")


if __name__ == "__main__":
    main()
