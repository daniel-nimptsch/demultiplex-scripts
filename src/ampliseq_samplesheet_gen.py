import os
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="""
            Generate a sample sheet from filenames originating from demultiplex
            cutadapt script in a directory.
            """
    )
    parser.add_argument(
        "directory",
        type=str,
        help="""
            The directory containing the files. Files are expected to have this
            format: {sample_name}_R{1,2}.fastq.gz
            """,
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="The output file to write the sample sheet to. If not provided, output will be printed to the console.",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="The output file to write the sample sheet to. If not provided, output will be printed to the console.",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Directory {args.directory} does not exist.")
        exit(1)

    output = []
    output.append("sampleID,forwardReads,reverseReads")
    sample_dict = parse_directory(args.directory)
    output = generate_output(sample_dict, args)

    if args.output:
        with open(args.output, "w") as f:
            f.write("\n".join(output) + "\n")
    else:
        print("\n".join(output))


def parse_directory(directory):
    sample_dict = {}
    for filename in os.listdir(directory):
        if filename.endswith(".fastq.gz"):
            sample_name = "_".join(filename.split("_")[:-1])
            if sample_name not in sample_dict:
                sample_dict[sample_name] = {"R1": None, "R2": None}
            if "_R1" in filename:
                sample_dict[sample_name]["R1"] = os.path.join(directory, filename)
            elif "_R2" in filename:
                sample_dict[sample_name]["R2"] = os.path.join(directory, filename)
    return sample_dict


def generate_output(sample_dict, args):
    output = ["sampleID,forwardReads,reverseReads"]
    for sample_name, paths in sample_dict.items():
        if paths["R1"] and paths["R2"]:
            output.append(f"{sample_name},{paths['R1']},{paths['R2']}")
    if args.output:
        with open(args.output, "w") as f:
            f.write("\n".join(output) + "\n")
    else:
        print("\n".join(output))
    return output


if __name__ == "__main__":
    main()
