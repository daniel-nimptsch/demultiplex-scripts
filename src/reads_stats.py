import sys

def main():
    if len(sys.argv) > 2:
        print("Usage: python read_stats.py [<input_file>]")
        sys.exit(1)

    if len(sys.argv) == 2:
        input_file = sys.argv[1]
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines() # read file
        except FileNotFoundError:
            print(f"File {input_file} not found.")
            sys.exit(1)
    else:
        lines = sys.stdin.readlines() # stdin

    total_reads = 0
    data = []

    for line in lines:
        parts = line.strip().split('\t') # split by tab
        if len(parts) != 2: # if line has more tha 2 columns
            continue
        filename, read_count = parts
        read_count = int(read_count)
        data.append((filename, read_count))
        total_reads += read_count

    if total_reads == 0:
        print("No reads found.")
        sys.exit(1)

    print("filename\treads\trelative_reads")
    for filename, read_count in data:
        relative_read_count = read_count / total_reads
        print(f"{filename}\t{read_count}\t{relative_read_count:.6f}")

    print(f"Total\t{total_reads}\t1.000000")

if __name__ == "__main__":
    main()
