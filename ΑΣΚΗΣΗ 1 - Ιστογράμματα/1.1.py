#Vasileios Pistikopoulos 5336
#Evagelos Vaitsis 5096
import matplotlib.pyplot as plt

def load_ages(filename="final_general.dat"):
    ages = []
    with open(filename, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                age = int(parts[1])
                ages.append(age)
            except ValueError:
                continue
    return ages

#φτιαχνει histogram με bins ισου πλατους
def equiwidth(ages, bins):
    min_age = min(ages)
    max_age = max(ages)
    width = (max_age - min_age) / bins #υποπολογιζει πλατος 

    hist = [0] * bins #αρχικοποιηση της λιστας των μετρητων για καθε bin
    for age in ages:
        index = int((age - min_age) / width) #βρισκει σε ποιο bin ανηκει η ηλικια
        if index == bins: #edge case για max_age 
            index -= 1
        hist[index] += 1 #αυξηση του καταλληλου μετρητη

    ranges = []
    for i in range(bins):#υπολογισμος των οριων καθε bin
        start = min_age + i * width
        end = start + width
        ranges.append((round(start, 1), round(end, 1)))

    return hist, ranges

#ιδιο πληθος στοιχειων σε καθε bin
def equidepth(ages, bins):
    sorted_ages = sorted(ages)# πρεπει να ειναι ταξινομημενες για να βρουμε τα ορια των bins
    n = len(sorted_ages)

    base_size = n // bins
    remainder = n % bins #αν δεν διαιρειται ακριβως, τα πρωτα 'remainder' bins θα εχουν ενα στοιχειο παραπανω

    boundaries = []#ορια
    sizes = []#ποσα στοιχεια σε καθε bin
    index = 0

    for i in range(bins - 1):
        size = base_size + (1 if i < remainder else 0)
        index += size
        sizes.append(size)
        boundaries.append(sorted_ages[index - 1])  # τελευταία τιμή του bin

    # τελευταίο bin
    sizes.append(n - sum(sizes))#παιρνει οτι εχει μεινει
    boundaries.append(sorted_ages[-1])

    return boundaries, sizes


def save_histograms(numofages, hist, ranges, boundaries, sizes, filename="histograms.txt"):
    with open(filename, "w") as f:
        f.write(f"Number of ages: {numofages}\n\n")

        f.write("Equi-width histogram (count per bin with ranges):\n\n")
        for i, (count, (start, end)) in enumerate(zip(hist, ranges), 1):
            f.write(f"Bin {i:2d} [{start:5.1f}, {end:5.1f}): {count}\n")

        f.write("\n")

        f.write("Equi-depth histogram (boundaries and counts):\n\n")
        prev = "min"
        for i, (b, c) in enumerate(zip(boundaries, sizes), 1):
            f.write(f"Bin {i:2d} [{prev}, {b}]: count={c}\n")
            prev = b + 1
        f.write("\n")


def plot_histograms(hist, ranges, boundaries, sizes, min_age, max_age, filename="histograms.png"):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # εqui-width
    labels_ew = [f"{int(s)}-{int(e)}" for s, e in ranges]
    ax1.bar(labels_ew, hist, color="steelblue", edgecolor="white")
    ax1.set_title("Equi-width Histogram")
    ax1.set_xlabel("Age Range")
    ax1.set_ylabel("Count")
    ax1.tick_params(axis="x", rotation=45)

    #Equi-depth 
    labels_ed = []
    prev = min_age
    for b in boundaries[:-1]:
        labels_ed.append(f"{prev}-{b}")
        prev = b + 1
    labels_ed.append(f"{prev}-{max_age}")

    ax2.bar(labels_ed, sizes, color="steelblue", edgecolor="white")
    ax2.set_title("Equi-depth Histogram")
    ax2.set_xlabel("Age Range")
    ax2.set_ylabel("Count")
    ax2.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Γράφημα αποθηκεύτηκε: {filename}")


def main():
    bins = 10
    ages = load_ages()
    num_of_ages = len(ages)

    hist, ranges = equiwidth(ages, bins)
    boundaries, sizes = equidepth(ages, bins)

    save_histograms(num_of_ages, hist, ranges, boundaries, sizes)
    print("Τα δεδομένα αποθηκεύτηκαν: histograms.txt και τα γραφήματα: histograms.png")

    plot_histograms(hist, ranges, boundaries, sizes, min(ages), max(ages))


if __name__ == "__main__":
    main()