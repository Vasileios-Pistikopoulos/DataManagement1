import sys
import csv

# PART 2.1 - SEMIJOIN (κραταει τα tuples του r που έχουν αντιστοιχία στο s)

#υλοπο;ιηση sort-merge semijoin 
def sort_merge_semijoin(r, s):
    #ταξινομηση με βαση το join key (πρωτο πεδιο)
    r_sorted = sorted(r, key=lambda x: x[0])
    s_sorted = sorted(s, key=lambda x: x[0])

    #i για r j για s
    i = j = 0
    result = []

    while i < len(r_sorted) and j < len(s_sorted):
        if r_sorted[i][0] == s_sorted[j][0]:#αν ταιριαζουν
            key = r_sorted[i][0]#κρατα το key
            while i < len(r_sorted) and r_sorted[i][0] == key:#κρατα και ολα οσα εχουν το key
                result.append(r_sorted[i])
                i += 1
            while j < len(s_sorted) and s_sorted[j][0] == key:#απλα προχωραω στο s (αριστερη συννενωση)
                j += 1
        elif r_sorted[i][0] < s_sorted[j][0]:#αν το key του r ειναι μικροτερο, προχωρα  r
            i += 1
        else:#αλλιως προχωρα s
            j += 1

    return result

def hash_semijoin(r, s):
    hash_table = {}#δηιουργια dictionary για τα keys του s
    result = []#array για το αποτελεσμα
    for t in s:#για καθε tuple του s
        key = t[0]#παρε κλειδι
        if key not in hash_table:#αν δεν ειναι βαλτο στο dict
            hash_table[key] = True
   
    for t in r:#για καθε tuple του r
        key = t[0]#παρε κλειδι
        if key in hash_table:#αν το κλειδι υπαρχει στο table με τα keys του s
            result.append(t)#προσθεσε στο αποτελεσμα

    return result


# PART 2.1 - ANTI-SEMIJOIN (κρατα απο το r μονο οσα ΔΕΝ εχουν αντιστοιχια στο s)
def sort_merge_antisemijoin(r, s):
    #ταξινομηση με βαση το join key (πρωτο πεδιο)
    r_sorted = sorted(r, key=lambda x: x[0])
    s_sorted = sorted(s, key=lambda x: x[0])

    i = j = 0
    result = []
    #ιδια λογικη με το semijoin, αλλα προσθετουμε στο αποτελεσμα οταν δεν ταιριαζουν
    while i < len(r_sorted) and j < len(s_sorted):
        if r_sorted[i][0] == s_sorted[j][0]:#αν βρω ταιριασμα, προχωραω και στα δυο
            key = r_sorted[i][0]
            while i < len(r_sorted) and r_sorted[i][0] == key:
                i += 1
            while j < len(s_sorted) and s_sorted[j][0] == key:
                j += 1
        elif r_sorted[i][0] < s_sorted[j][0]:#αν το key του r ειναι μικροτερο, προσθεσε το στο αποτελεσμα και προχωρα r
            result.append(r_sorted[i])
            i += 1
        else:#αν το s εμεινει πισω, προχωρα s
            j += 1
    #θα μεινουν στο r ολα τα tuples που δεν βρηκαν ταιριασμα στο s, προσθετουμε και αυτα στο αποτελεσμα
    while i < len(r_sorted):
        result.append(r_sorted[i])
        i += 1

    return result

def hash_antisemijoin(r, s):
    #φτιάχνω dict για τα keys του S
    hash_table = {}
    for t in s:
        key = t[0]
        if key not in hash_table:
            hash_table[key] = True #βαλε ολα τα κλειδια του s στο dict

    # κρατάω από το R όσα ΔΕΝ έχουν match
    result = []
    for t in r:
        key = t[0]
        if key not in hash_table:
            result.append(t)

    return result


# LOAD DATA

def load_airports():
    #Join key: parts[0] = ID αεροδρομίου 
    r = []
    with open("airports.dat", encoding="utf-8") as f:
        reader = csv.reader(f)
        for parts in reader:
            if len(parts) > 0 and parts[0] not in ("\\N", ""):
                try:
                    r.append((int(parts[0]), parts))
                except ValueError:
                    continue
    return r


def load_routes():
    #Join key: parts[5] = ID προορισμού
    s = []
    with open("routes.dat", encoding="utf-8") as f:
        reader = csv.reader(f)
        for parts in reader:
            if len(parts) > 5 and parts[5] not in ("\\N", ""):
                try:
                    s.append((int(parts[5]), parts))
                except ValueError:
                    continue
    return s


# PART 2.2 - SELECTION + SORT-MERGE SEMIJOIN

def airports_with_aircraft(aircraft_type):
    """
    Selection: routes με τον συγκεκριμένο τύπο αεροσκάφους (τελευταίο πεδίο)
    Join key: airports parts[0], routes parts[5] (IDs)
    """
    
    airports = []
    with open("airports.dat", encoding="utf-8") as f:
        reader = csv.reader(f)
        for parts in reader:
            if len(parts) > 0 and parts[0] not in ("\\N", ""):
                try:
                    airports.append((int(parts[0]), parts))
                except ValueError:
                    continue
    #(δινεται οτι ειναι sorted)
    
    # φορτωση και sort routes
    routes = []
    with open("routes.dat", encoding="utf-8") as f:
        reader = csv.reader(f)
        for parts in reader:
            if (len(parts) > 5 and parts[5] not in ("\\N", "")
                    and aircraft_type in parts[-1].strip().split()):
                try:
                    routes.append((int(parts[5]), parts))
                except ValueError:
                    continue

    routes_sorted  = sorted(routes, key=lambda x: x[0])

   # Χρησιμοποιώ την sort-merge semijoin που έχω ορίσει παραπάνω
    return sort_merge_semijoin(airports, routes_sorted)


# PART 2.3 - PIPELINED MERGE JOIN

def pipelined_merge_join(r, s, t):
    """
    join(r,s) με pipeline: κάθε πλειάδα join(r,s) συνενώνεται
    αμέσως με t χωρίς αποθήκευση ενδιάμεσου αποτελέσματος.
    """
    result = []
    i = j = k = 0

    while i < len(r) and j < len(s):
        if r[i][0] == s[j][0]:#αν match στα r και s
            key = r[i][0]

            r_group = []#ολα τα tuples του r με το key
            while i < len(r) and r[i][0] == key:
                r_group.append(r[i])
                i += 1

            s_group = []#ολα τα tuples του s με το key
            while j < len(s) and s[j][0] == key:
                s_group.append(s[j])
                j += 1

            while k < len(t) and t[k][0] < key:#προχωρα στο t μεχρι να φτασεις στο key
                k += 1

            # pipeline: αμέσως join με t, χωρίς αποθήκευση join(r,s)
            if k < len(t) and t[k][0] == key:#αν match και στο t
                k_temp = k
                while k_temp < len(t) and t[k_temp][0] == key:
                    for r_tuple in r_group:#για καθε συνδυασμο των r και s με το ιδιο key, προσθεσε στο αποτελεσμα το join με ολα τα t που εχουν το ιδιο key
                        for s_tuple in s_group:
                            result.append((key, r_tuple[1], s_tuple[1], t[k_temp][1]))
                    k_temp += 1

        elif r[i][0] < s[j][0]:#αν το key του r ειναι μικροτερο, προχωρα r
            i += 1
        else:#αν το key του s ειναι μικροτερο, προχωρα s
            j += 1

    return result


# PART 2.3 - THREE-WAY SORT-MERGE JOIN

def three_way_sort_merge_join(r, s, t):
    i = j = k = 0
    result = []

    while i < len(r) and j < len(s) and k < len(t):
        a_r = r[i][0]
        a_s = s[j][0]
        a_t = t[k][0]

        if a_r == a_s == a_t:#αν ολα τα keys ταιριαζουν
            key = a_r

            r_group = []#ολα τα tuples του r με το key
            while i < len(r) and r[i][0] == key:
                r_group.append(r[i])
                i += 1

            s_group = []#ολα τα tuples του s με το key
            while j < len(s) and s[j][0] == key:
                s_group.append(s[j])
                j += 1

            t_group = []#ολα τα tuples του t με το key
            while k < len(t) and t[k][0] == key:
                t_group.append(t[k])
                k += 1

            for r_t in r_group:#για καθε συνδυασμο των r, s και t με το ιδιο key, προσθεσε στο αποτελεσμα
                for s_t in s_group:
                    for t_t in t_group:
                        result.append((key, r_t[1], s_t[1], t_t[1]))
        else:#αν δεν ταιριαζουν τα keys, προχωρα σε αυτα που εχουν το μικροτερο key
            min_key = min(a_r, a_s, a_t)
            if a_r == min_key:
                i += 1
            if a_s == min_key:
                j += 1
            if a_t == min_key:
                k += 1

    return result


if __name__ == "__main__":

    #PART 2.1: test 
    print("PART 2.1 kanoume ena test")
    r_test = [(1,2),(1,4),(2,5)]
    s_test = [(1,'a'),(1,'c'),(3,'a')]
    print("r =", r_test)
    print("s =", s_test)
    print("sort_merge_semijoin:    ", sort_merge_semijoin(r_test, s_test))
    print("hash_semijoin:          ", hash_semijoin(r_test, s_test))
    print("sort_merge_antisemijoin:", sort_merge_antisemijoin(r_test, s_test))
    print("hash_antisemijoin:      ", hash_antisemijoin(r_test, s_test))

    #PART 2.1: πραγματικά δεδομένα
    print()
    print("PART 2.1")
    airports = load_airports()
    routes = load_routes()
    print(f"sort_merge_semijoin:     {len(sort_merge_semijoin(airports, routes))} αεροδρόμια")
    print(f"hash_semijoin:           {len(hash_semijoin(airports, routes))} αεροδρόμια")
    print(f"sort_merge_antisemijoin: {len(sort_merge_antisemijoin(airports, routes))} αεροδρόμια")
    print(f"hash_antisemijoin:       {len(hash_antisemijoin(airports, routes))} αεροδρόμια")

    #PART 2.2
    print()
    print("PART 2.2")
    aircraft_type = sys.argv[1] if len(sys.argv) > 1 else "SU9"#default
    result_22 = airports_with_aircraft(aircraft_type)
    print(f"Τύπος αεροσκάφους: {aircraft_type}")
    print(f"Αεροδρόμια που βρέθηκαν: {len(result_22)}")
    for row in result_22:
        print(",".join(map(str, row)))

    #PART 2.3
    print()
    print("PART 2.3")
    r3 = [(1,'b1'),(2,'b2'),(3,'b3'),(4,'b4')]
    s3 = [(1,'c1'),(1,'c2'),(2,'c3'),(3,'c4')]
    t3 = [(1,'d1'),(2,'d2'),(3,'d3'),(5,'d4')]
    print("r =", r3)
    print("s =", s3)
    print("t =", t3)
    print("\npipelined_merge_join(r,s,t):")
    for row in pipelined_merge_join(r3, s3, t3):
        print(" ", row)
    print("\nthree_way_sort_merge_join(r,s,t):")
    for row in three_way_sort_merge_join(r3, s3, t3):
        print(" ", row)