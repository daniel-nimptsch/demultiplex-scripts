import argparse
import csv

def main():
    parser = argparse.ArgumentParser(description="Process a samplesheet in CSV format.")
    parser.add_argument('samplesheet', type=str, help='Path to the samplesheet CSV file')

    args = parser.parse_args()

    samplesheet = args.samplesheet
    with open(samplesheet, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            print(row)  # Replace this with your actual processing logic

if __name__ == "__main__":
    main()
