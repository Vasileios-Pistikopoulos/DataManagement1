
import re

def read_histograms(filename="histograms.txt"):
    hist = []
    ranges = []
    boundaries = []
    counts = []

    with open(filename, "r") as f:
        lines = f.readlines()

    section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "Equi-width" in line:
            section = "width"
            continue
        elif "Equi-depth" in line:
            section = "depth"
            continue
        elif "Number of ages" in line:
            continue

        if section == "width":
            match = re.search(r'\(([\d.]+), ([\d.]+)\): (\d+)', line)
            if match:
                start = float(match.group(1))
                end = float(match.group(2))
                count = int(match.group(3))
                ranges.append((start, end))
                hist.append(count)
        elif section == "depth":
            match = re.search(r'max=(\d+), count=(\d+)', line)
            if match:
                bound = int(match.group(1))
                count = int(match.group(2))
                boundaries.append(bound)
                counts.append(count)

    return hist, ranges, boundaries, counts

def estimate_equiwidth(hist, ranges, a, b):
    estimated = 0
    for count, (start, end) in zip(hist, ranges):
        overlap_start = max(start, a)
        overlap_end = min(end, b)
        fraction = max(0, (overlap_end - overlap_start) / (end - start))
        estimated += count * fraction
    return estimated

def estimate_equidepth(boundaries, counts, a, b, min_age):
    estimated = 0
    for i, (bound, count) in enumerate(zip(boundaries, counts)):
        bin_start = min_age if i == 0 else boundaries[i-1] + 1
        bin_end = bound
        overlap_start = max(bin_start, a)
        overlap_end = min(bin_end, b)
        fraction = max(0, (overlap_end - overlap_start) / (bin_end - bin_start))
        estimated += count * fraction
    return estimated

def load_ages(filename="final_general.dat"):
    ages = []
    with open(filename, "r") as f:
        for line in f:
            parts = line.split()
            age = int(parts[1])
            ages.append(age)
    return ages

def main():
    hist, ranges, boundaries, counts = read_histograms("histograms.txt")
    ages = load_ages()
    min_age = min(ages)

    a = int(input("Enter a (lower bound of Age): "))
    b = int(input("Enter b (upper bound of Age): "))

    est_width = estimate_equiwidth(hist, ranges, a, b)
    est_depth = estimate_equidepth(boundaries, counts, a, b, min_age)
    real = sum(1 for age in ages if a <= age <= b)

    print(f"\nInterval [{a}, {b}]")
    print(f"Estimated (Equi-width): {est_width:.1f}")
    print(f"Estimated (Equi-depth): {est_depth:.1f}")
    print(f"Actual: {real}")

if __name__ == "__main__":
    main()