import subprocess


def get_help_output(script_path):
    result = subprocess.run(
        ["python", script_path, "--help"], capture_output=True, text=True
    )
    return result.stdout


def main():
    scripts = [
        "src/parse_samplesheet_novogene.py",
        "src/barcodes_to_fasta.py",
        "src/demultiplex.py",
        "src/ampliseq_samplesheet_gen.py",
        "src/patterns_copy.py",
        "src/dir_to_reads_tsv.sh",
    ]

    readme_content = """
        # Demultiplex scripts

        This repository contains scripts to demultiplex sequencing data using
        cutadapt and to generate a sample sheet for nf-core/ampliseq.

        ## Usage

        Take a look at the example pipeline in `src/example_pipeline.sh`. This
        shows you how the scripts can be used in conjunction.

        """

    for script in scripts:
        help_output = get_help_output(script)
        readme_content += f"### {script}\n\n"
        readme_content += "```\n"
        readme_content += help_output
        readme_content += "```\n\n"

    with open("README.md", "w") as readme_file:
        readme_file.write(readme_content)


if __name__ == "__main__":
    main()
