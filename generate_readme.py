import subprocess


def get_help_output(script_path):
    if script_path.endswith(".py"):
        result = subprocess.run(
            ["python", script_path, "--help"], capture_output=True, text=True
        )
    elif script_path.endswith(".sh"):
        result = subprocess.run(
            ["bash", script_path, "--help"], capture_output=True, text=True
        )
    else:
        raise ValueError(f"Unsupported script type: {script_path}")
    return result.stdout


def main():
    scripts = [
        "src/pipeline.sh",
        "src/read_counts.py",
        "src/motif_counts.py",
        "src/parse_samplesheet_novogene.py",
        "src/barcodes_to_fasta.py",
        "src/demultiplex.py",
        "src/patterns_copy.py",
        "src/ampliseq_samplesheet_gen.py",
    ]

    readme_content = """# Demultiplex scripts

This repository contains scripts to demultiplex sequencing data using
cutadapt and to generate a sample sheet for nf-core/ampliseq.

## Installation

Install the required dependencies with either conda or mamba. Use:
`environment.yml`. For example:

```bash
mamba env create -f environment.yml
```

Activate the env before executing the pipeline:

```bash
mamba activate demultiplex-scripts
```

## Usage

The main pipeline script is `src/pipeline.sh`. Here's its usage information:

"""
    pipeline_help = get_help_output("src/pipeline.sh")
    readme_content += "```\n"
    readme_content += pipeline_help
    readme_content += "```\n\n"

    readme_content += "## Individual Scripts\n\n"
    readme_content += "The following scripts are used within the pipeline:\n\n"

    for script in scripts[1:]:  # Skip pipeline.sh as it's already been added
        help_output = get_help_output(script)
        readme_content += f"### {script}\n\n"
        readme_content += "```\n"
        readme_content += help_output
        readme_content += "```\n\n"

    with open("README.md", "w") as readme_file:
        readme_file.write(readme_content)


if __name__ == "__main__":
    main()
