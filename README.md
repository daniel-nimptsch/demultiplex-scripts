# Demultiplex scripts

This repository contains scripts to demultiplex sequencing data using
cutadapt and to generate a sample sheet for nf-core/ampliseq.

## Usage

Take a look at the example pipeline in `src/example_pipeline.sh`. This
shows you how the scripts can be used in conjunction.


### src/read_counts.py

```
usage: read_counts.py [-h] [-o OUTPUT] input_path

Count reads in a dir of input FASTA/FASTQ files.

positional arguments:
  input_path            Path to the directory containing FASTA/FASTQ files

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory path. Default is current directory.
```

### src/motif_counts.py

```
usage: motif_counts.py [-h] [-o OUTPUT] [-v] [-w] input_path barcode primer

Count subset of reads with specific adapter or primer sequences in input
FASTA/FASTQ files.

positional arguments:
  input_path            Path to the input path with fastq files.
  barcode               Path to the barcode FASTA file
  primer                Path to the primer FASTA file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory path. Default is current directory.
  -v, --verbose         Print seqkit commands and their outputs
  -w, --write-to-file   Write result to a TSV file. Default is False.
```

### src/parse_samplesheet_novogene.py

```
usage: parse_samplesheet_novogene.py [-h] samplesheet_path

Parse a samplesheet and print barcodes in TSV format. This is a specific
parsing script for novogene multiplex sample sheet.

positional arguments:
  samplesheet_path  Path to the samplesheet file

options:
  -h, --help        show this help message and exit
```

### src/barcodes_to_fasta.py

```
usage: barcodes_to_fasta.py [-h] [--include-primers] [-o OUTPUT] [samplesheet]

Generate FASTA files from a samplesheet (TSV) containing sample names and
barcodes. The samplesheet should be tab-delimited with the following format:
sample name, forward barcode, reverse barcode, forward barcode name, reverse
barcode name, forward primer, reverse primer, and primer name. Additionally a
patterns file is generated for the use after cutadapts demultiplex of paired-
end reads with combinatorial dual indexes. The patterns file can be used as
input with patterns_copy.py.

positional arguments:
  samplesheet           Path to the samplesheet TSV (default: stdin)

options:
  -h, --help            show this help message and exit
  --include-primers     Include primers in the barcodes saved to the FASTA
                        files (default: False)
  -o OUTPUT, --output OUTPUT
                        Directory to save the output FASTA files (default: ./)
```

### src/demultiplex.py

```
usage: demultiplex.py [-h] [-o OUTPUT] [-c] [-e ERROR_RATE]
                      [--min-overlap MIN_OVERLAP]
                      fq_gz_1 fq_gz_2 forward_fasta reverse_fasta

Demultiplex with cutadapt paired end FASTQ files using forward and reverse
FASTA files containing barcodes. You have the option between the default mode
where paired adapters with unique dual indices are assumed and the mode
combinatorial dual indexes for demultiplexing.

positional arguments:
  fq_gz_1               Path to the first FASTQ file (R1)
  fq_gz_2               Path to the second FASTQ file (R2)
  forward_fasta         Path to the forward FASTA file containing barcodes
  reverse_fasta         Path to the reverse FASTA file containing barcodes

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Directory to save the output demultiplexed FASTQ files
                        (default: ./)
  -c, --combinatorial   Use combinatorial dual indexes for demultiplexing
                        paired-end reads (default: False). In the default case
                        demultiplexing unique dual indices is executed.
  -e ERROR_RATE, --error-rate ERROR_RATE
                        Maximum expected error rate (default: 0.14)
  --min-overlap MIN_OVERLAP
                        Minimum overlap length for adapter matching (default:
                        3)
```

### src/patterns_copy.py

```
usage: patterns_copy.py [-h] [-o OUTPUT] [patterns]

Rename files based on patterns provided either as an argument or from stdin.
The patterns should be a piar of words separated by space with each line of
the file being one pair. The first name should match a filepath and the second
is the filepath that the file will be copied to.

positional arguments:
  patterns              Path to the patterns file (default: stdin)

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        The output dir to copy the renamed. If not provided,
                        output will be ./.
```

### src/ampliseq_samplesheet_gen.py

```
usage: ampliseq_samplesheet_gen.py [-h] [-o OUTPUT] directory

Generate an ampliseq compatible sample sheet from filenames originating from
demultiplex cutadapt script in a directory.

positional arguments:
  directory             The directory containing the files. Files are expected
                        to have this format: {sample_name}_R{1,2}.fastq.gz

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        The output file to write the sample sheet to. If not
                        provided, output will be printed to the console.
```

