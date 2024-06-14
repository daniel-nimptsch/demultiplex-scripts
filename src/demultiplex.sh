#!/usr/bin/bash

cutadapt -e 2 --pair-adapters --cores=0 \
	-g ^file:data/multiplex/sample_sheet_agr_UPA_bc_fwd.fasta \
	-G ^file:data/multiplex/sample_sheet_agr_UPA_bc_rev.fasta \
	-o 'data/demultiplex/demux-{name}_R1.fastq.gz' \
	-p 'data/demultiplex/demux-{name}_R2.fastq.gz' \
	data/multiplex/AgroSoil_1_FKDN240147590-1A_H7HKJDRX5_L2_1.fq.gz \
	data/multiplex/AgroSoil_1_FKDN240147590-1A_H7HKJDRX5_L2_2.fq.gz
