import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python read_stats.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File {input_file} not found.")
        sys.exit(1)

    total_reads = 0
    data = []

    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) != 2:
            continue
        filename, read_count = parts
        read_count = int(read_count)
        data.append((filename, read_count))
        total_reads += read_count

    if total_reads == 0:
        print("No reads found.")
        sys.exit(1)

    print("Filename\tRead Count\tRelative Read Count")
    for filename, read_count in data:
        relative_read_count = read_count / total_reads
        print(f"{filename}\t{read_count}\t{relative_read_count:.6f}")

    print(f"Total\t{total_reads}\t1.000000")

if __name__ == "__main__":
    main()
