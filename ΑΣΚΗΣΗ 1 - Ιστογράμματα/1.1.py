def load_ages(filename="final_general.dat"):
    ages = []
    with open(filename, "r") as f:
        for line in f:
            parts = line.split()        
            age = int(parts[1])
            ages.append(age)   
    return ages

# bins εχουν ιδιο ευρος τιμων, και καθε bin οσες τιμες πεφτουν στο ευρος
def equiwidth(ages, bins):
    min_age = min(ages)
    max_age = max(ages)

    width = (max_age - min_age) / bins

    hist = [0] * bins
    ranges = []

    for age in ages:
        index = int((age - min_age) / width) #βρισκω σε ποιο index των bin ανηκει (αποσταση απο min, διαιρεση με bin width και μετατροπη σε ακεραιο)
        if index == bins:  # edge case για max για να μην μεινει εκτος (θα εβγαινε εκτος οριων)
            index -= 1
        hist[index] += 1 #αυξανω τα ποσα ειδα σε αυτο το bin

    # ranges για κάθε bin
    for i in range(bins):
        start = min_age + i * width
        end = start + width
        ranges.append((round(start,1), round(end,1)))

    return hist, ranges
#kaue bin na exei idio arithmo apo stoixeion
def equidepth(ages, bins):
    
    sorted_ages = sorted(ages)
    n = len(sorted_ages)
    sizes = [] #ποσα στοιχεια θα εχει τελικα το καθε bin

    base_size = n // bins
    remainder = n % bins #λογω ακεραιας διαιρεσης καποια μπορει να μεινουν απεξω

    boundaries = []
    index = 0

    for i in range(bins - 1):
        size = base_size
        if i < remainder:
            size += 1# για καθε ενα που περισεψε τα μοιραζουμε ισοτιμα στα πρωτα remainder bins
        index += size
        sizes.append(size)
        boundaries.append(sorted_ages[index])

    return boundaries,sizes

def save_histograms(numofages,hist, ranges, boundaries, sizes, filename="histograms.txt"):
    with open(filename, "w") as f:
        #number of ages total
        f.write(f"Number of ages: {numofages}\n\n")
        #equiwidth
        f.write("Equi-width histogram (count per bin with ranges):\n\n")
        for i, (count, (start, end)) in enumerate(zip(hist, ranges), 1):
            f.write(f"Bin {i} ({start:.1f}, {end:.1f}): {count}\n")
        f.write("\n")
        #equidepth
        f.write("Equi-depth histogram (boundaries and counts):\n\n")
        for i, (b, c) in enumerate(zip(boundaries, sizes), 1):
            f.write(f"Bin {i}: max={b}, count={c}\n")

def main():
    bins = 10
    ages = load_ages()
    num_of_ages = len(ages)
    hist, ranges = equiwidth(ages, bins)
    boundaries, sizes = equidepth(ages, bins)

    # αποθήκευση σε αρχείο
    save_histograms(num_of_ages,hist, ranges, boundaries,sizes)

if __name__ == "__main__":
    main()