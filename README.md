# Ampliseq Pipeline

This repository contains scripts to process sequencing data using cutadapt and generate sample sheets for ampliseq.

## Usage

### Step 1: Parse Novogene Samplesheet

Parse a samplesheet and print barcodes in TSV format. This is a specific parsing script for novogene multiplex sample sheet.

```bash
python src/parse_samplesheet_novogene.py PATH_TO_NOVOGENE_SAMPLESHEET
```

### Step 2: Generate FASTA Files from Samplesheet

Generate FASTA files from a samplesheet (TSV) containing sample names and barcodes. The samplesheet should be tab-delimited with the following format: sample name, forward barcode, reverse barcode, forward barcode name, reverse barcode name, forward primer, and reverse primer.

Additionally, a patterns file is generated for use after cutadapt's demultiplex of paired-end reads with combinatorial dual indexes. The patterns file can be used as input with `patterns_copy.py`.

```bash
python src/barcodes_to_fasta.py -o data/demultiplex
```

### Step 3: Demultiplex with Cutadapt

Demultiplex with cutadapt paired-end FASTQ files using forward and reverse FASTA files containing barcodes. You have the option between the default mode where paired adapters with unique dual indices are assumed and the mode combinatorial dual indexes for demultiplexing.

```bash
python src/demultiplex.py PATH_TO_FWD_FASTQ PATH_TO_REV_FASTQ data/demultiplex/barcodes_fwd.fasta data/demultiplex/barcodes_rev.fasta -o data/demultiplex -c
```

### Step 4: Rename Files Based on Patterns

Rename files based on patterns provided either as an argument or from stdin. The patterns should be a pair of words separated by space with each line of the file being one pair. The first name should match a filepath and the second is the filepath that the file will be copied to.

```bash
cat data/demultiplex/patterns.txt | python src/patterns_copy.py -o data/demultiplex/demux_renamed
```

### Step 5: Move Files to Work Directory

Move the demultiplexed FASTQ files to a work directory.

```bash
mkdir data/demultiplex/work
mv data/demultiplex/*.fastq.gz data/demultiplex/work/
```

### Step 6: Generate Read Counts

Generate read counts for the demultiplexed FASTQ files.

```bash
bash src/dir_to_reads_tsv.sh data/demultiplex/work > data/demultiplex/cutadapt_reads.tsv
bash src/dir_to_reads_tsv.sh data/demultiplex/demux_renamed > data/demultiplex/sample_reads.tsv
```

### Step 7: Generate Ampliseq Sample Sheet

Generate an ampliseq compatible sample sheet from filenames originating from demultiplex cutadapt script in a directory.

```bash
python src/ampliseq_samplesheet_gen.py data/demultiplex/demux_renamed > data/demultiplex/demux_renamed/sample_sheet.csv
```

## Example Pipeline

The following script demonstrates the entire pipeline:

```bash
#!/bin/bash

python src/parse_samplesheet_novogene.py PATH_TO_NOVOGENE_SAMPLESHEET | \
    python src/barcodes_to_fasta.py -o data/demultiplex

python src/demultiplex.py \
    PATH_TO_FWD_FASTQ \
    PATH_TO_REV_FASTQ \
    data/demultiplex/barcodes_fwd.fasta \
    data/demultiplex/barcodes_rev.fasta \
    -o data/demultiplex \
    -c

cat data/demultiplex/patterns.txt | \
    python src/patterns_copy.py -o data/demultiplex/demux_renamed

mkdir data/demultiplex/work
mv data/demultiplex/*.fastq.gz data/demultiplex/work/

bash src/dir_to_reads_tsv.sh data/demultiplex/work > data/demultiplex/cutadapt_reads.tsv
bash src/dir_to_reads_tsv.sh data/demultiplex/demux_renamed > data/demultiplex/sample_reads.tsv

python src/ampliseq_samplesheet_gen.py data/demultiplex/demux_renamed > \
    data/demultiplex/demux_renamed/sample_sheet.csv
```
