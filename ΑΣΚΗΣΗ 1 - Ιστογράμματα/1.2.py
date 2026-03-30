import re
import sys
#παραγει hist,ranges, boundaries και counts απο το αρχειο histograms.txt
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
            # διαβάζει γραμμές της μορφής: Bin  1 [ 14.0,  36.8): 123
            match = re.search(r'\[\s*([\d.]+),\s*([\d.]+)\):\s*(\d+)', line)
            if match:
                start = float(match.group(1))
                end   = float(match.group(2))
                count = int(match.group(3))
                ranges.append((start, end))
                hist.append(count)

        elif section == "depth":
            # διαβάζει γραμμές της μορφής: Bin  1 [min, 25]: count=123
            match = re.search(r'\[(.+),\s*(\d+)\]:\s*count=(\d+)', line)
            if match:
                bound = int(match.group(2))
                count = int(match.group(3))
                boundaries.append(bound)
                counts.append(count)

    return hist, ranges, boundaries, counts


def estimate_equiwidth(hist, ranges, a, b):
    estimated = 0.0
    for count, (start, end) in zip(hist, ranges): #για καθε bin
        if end <= a or start > b:#αν ειναι εξω απο το διαστημα, αγνοησε
            continue
        overlap_start = max(start, a) #το σημειο που ξεκιναει η επικαλυψη του bin με το διαστημα
        overlap_end   = min(end, b + 1) # +1 γιατί το β είναι inclusive
        fraction = (overlap_end - overlap_start) / (end - start)#το ποσο του bin που επικαλυπτεται με το διαστημα
        estimated += count * fraction #θεωρω ομοιομορφη κατανομη μεσα στο bin και προσθετω το αναλογο μερος του count στο αποτελεσμα
    return estimated


def estimate_equidepth(boundaries, counts, a, b):
    estimated = 0.0

    for i, (bound, count) in enumerate(zip(boundaries, counts)):#για καθε bin (bound = τελος, count = ποσα στοιχεια εχει)
        if i == 0:
            bin_start = boundaries[0] - (boundaries[1] - boundaries[0]) #υποθετω οτι πλατος πρωτου bin ειναι ιδιο με του δευτερου
        else:
            bin_start = boundaries[i - 1] + 1 #το bin ξεκιναει απο το επομενο του προηγουμενου boundary
        
        bin_end = bound

        if bin_end < a or bin_start > b:#αν το bin ειναι εξω απο το διαστημα, αγνοησε
            continue
        
        #ορια επικαλυψης του bin με το διαστημα
        overlap_start = max(bin_start, a)
        overlap_end = min(bin_end, b)

        bin_width = bin_end - bin_start + 1# +1 για inclusive boundaries
        fraction = (overlap_end - overlap_start + 1) / bin_width# τι ποσοστο καλυπτει το ζητουμενο διαστημα

        estimated += count * fraction

    return estimated


def load_ages(filename="final_general.dat"):
    ages = []
    with open(filename, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                ages.append(int(parts[1]))
            except ValueError:
                continue
    return ages


def main():
    hist, ranges, boundaries, counts = read_histograms("histograms.txt")

    if not hist or not boundaries:
        print("Σφάλμα: δεν διαβάστηκαν δεδομένα από το histograms.txt")
        print(f"  equi-width bins διαβάστηκαν: {len(hist)}")
        print(f"  equi-depth bins διαβάστηκαν: {len(boundaries)}")
        sys.exit(1)

    ages = load_ages()

    try:
        a = int(input("Δώσε a (κάτω όριο): "))
        b = int(input("Δώσε b (άνω όριο): "))
    except ValueError:
        print("Σφάλμα: δώσε ακέραιους αριθμούς.")
        sys.exit(1)

    if a > b:
        print("Σφάλμα: το a πρέπει να είναι <= b")
        sys.exit(1)

    est_width = estimate_equiwidth(hist, ranges, a, b)
    est_depth = estimate_equidepth(boundaries, counts, a, b)
    real = sum(1 for age in ages if a <= age <= b)# μετράει πόσες ηλικίες είναι στο διάστημα [a, b]

    print(f"\nΔιάστημα [{a}, {b}]")
    print(f"Εκτίμηση equi-width:  {est_width:.1f}")
    print(f"Εκτίμηση equi-depth:  {est_depth:.1f}")
    print(f"Πραγματικό αποτέλεσμα: {real}")
    
    #
    if real > 0:
        err_w = abs(est_width - real) / real * 100
        err_d = abs(est_depth - real) / real * 100
        print(f"\nΣφάλμα equi-width:  {err_w:.1f}%")
        print(f"Σφάλμα equi-depth:  {err_d:.1f}%")

if __name__ == "__main__":
    main()