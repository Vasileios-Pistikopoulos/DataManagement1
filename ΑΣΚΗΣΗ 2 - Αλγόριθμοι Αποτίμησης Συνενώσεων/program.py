import sys
# -----------------------------
# PART 2.1
# SEMIJOIN
# -----------------------------

def sort_merge_semijoin(r, s):

    r_sorted = sorted(r, key=lambda x: x[0])
    s_sorted = sorted(s, key=lambda x: x[0])

    i = j = 0
    result = []

    while i < len(r_sorted) and j < len(s_sorted):

        if r_sorted[i][0] == s_sorted[j][0]:
            result.append(r_sorted[i])
            i += 1

        elif r_sorted[i][0] < s_sorted[j][0]:
            i += 1

        else:
            j += 1

    return result


def hash_semijoin(r, s):

    s_keys = {t[0] for t in s}

    result = []

    for t in r:
        if t[0] in s_keys:
            result.append(t)

    return result


# -----------------------------
# ANTI-SEMIJOIN
# -----------------------------

def hash_antisemijoin(r, s):

    s_keys = {t[0] for t in s}

    result = []

    for t in r:
        if t[0] not in s_keys:
            result.append(t)

    return result


def sort_merge_antisemijoin(r, s):

    r_sorted = sorted(r, key=lambda x: x[0])
    s_sorted = sorted(s, key=lambda x: x[0])

    i = j = 0
    result = []

    while i < len(r_sorted) and j < len(s_sorted):

        if r_sorted[i][0] < s_sorted[j][0]:
            result.append(r_sorted[i])
            i += 1

        elif r_sorted[i][0] > s_sorted[j][0]:
            j += 1

        else:
            i += 1

    while i < len(r_sorted):
        result.append(r_sorted[i])
        i += 1

    return result


# -----------------------------
# LOAD DATA
# -----------------------------

def load_airports():

    r = []

    with open("airports.dat", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",")

            if parts[0] != "\\N":
                r.append((parts[0], line.strip()))

    return r


def load_routes():

    s = []

    with open("routes.dat", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",")

            if len(parts) > 5 and parts[5] != "\\N":
                s.append((parts[5], line.strip()))

    return s


# -----------------------------
# PART 2.2
# selection + semijoin
# -----------------------------

import csv

def airports_with_aircraft(aircraft_type):
    # Φόρτωση airports
    airports = []
    with open("airports.dat", encoding="utf-8") as f:
        reader = csv.reader(f)
        for parts in reader:
            if parts[0] != "\\N":
                airports.append((int(parts[0]), ",".join(parts)))

    # Φόρτωση routes και επιλογή τύπου
    routes = []
    with open("routes.dat", encoding="utf-8") as f:
        reader = csv.reader(f)
        for parts in reader:
            if len(parts) > 8 and parts[5] != "\\N" and aircraft_type in parts[8].strip():
                routes.append((int(parts[5]), ",".join(parts)))

    # Sort-merge join
    airports
    routes_sorted = sorted(routes, key=lambda x: x[0])

    i = j = 0
    result = []

    while i < len(airports) and j < len(routes_sorted):
        airport_id = airports[i][0]
        route_dest = routes_sorted[j][0]

        if airport_id == route_dest:
            result.append(airports[i][1])

        # προχώρα όλα τα ίδια routes
            while j < len(routes_sorted) and routes_sorted[j][0] == airport_id:
                j += 1

            i += 1
        elif airport_id < route_dest:
            i += 1
        else:
            j += 1

    return result


# -----------------------------
# PART 2.3
# PIPELINED JOIN
# -----------------------------

def pipelined_merge_join(r, s, t):

    i = j = k = 0
    result = []

    while i < len(r) and j < len(s):

        if r[i][0] == s[j][0]:

            a = r[i][0]

            s_matches = []
            j_temp = j

            while j_temp < len(s) and s[j_temp][0] == a:
                s_matches.append(s[j_temp])
                j_temp += 1

            while k < len(t) and t[k][0] < a:
                k += 1

            if k < len(t) and t[k][0] == a:

                for s_tuple in s_matches:
                    result.append((a, r[i][1], s_tuple[1], t[k][1]))

            i += 1

        elif r[i][0] < s[j][0]:
            i += 1
        else:
            j += 1

    return result


# -----------------------------
# THREE-WAY MERGE JOIN
# -----------------------------

def three_way_sort_merge_join(r, s, t):

    i = j = k = 0
    result = []

    while i < len(r) and j < len(s) and k < len(t):

        a_r = r[i][0]
        a_s = s[j][0]
        a_t = t[k][0]

        if a_r == a_s == a_t:

            r_val = r[i][1]

            s_matches = []
            while j < len(s) and s[j][0] == a_r:
                s_matches.append(s[j])
                j += 1

            t_matches = []
            while k < len(t) and t[k][0] == a_r:
                t_matches.append(t[k])
                k += 1

            for s_tuple in s_matches:
                for t_tuple in t_matches:
                    result.append((a_r, r_val, s_tuple[1], t_tuple[1]))

            i += 1

        else:

            min_key = min(a_r, a_s, a_t)

            if a_r == min_key:
                i += 1
            elif a_s == min_key:
                j += 1
            else:
                k += 1

    return result


# MAIN
if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python script.py <aircraft_type>")
        sys.exit(1)

    
    aircraft_type = sys.argv[1]

    print("---- PART 2.1 TEST ----")

    r = [(1,2),(1,4),(2,5)]
    s = [(1,'a'),(1,'c'),(3,'a')]

    print("Semijoin:", hash_semijoin(r,s))
    print("Antisemijoin:", hash_antisemijoin(r,s))


    print("\n---- PART 2.1 REAL DATA ----")

    airports = load_airports()
    routes = load_routes()

    print("Semijoin airports-routes:", len(hash_semijoin(airports,routes)))
    print("Antisemijoin airports-routes:", len(hash_antisemijoin(airports,routes)))


    print("\n---- PART 2.2 TEST ----")

    aircraft_type = sys.argv[1]

    result = airports_with_aircraft(aircraft_type)

    print("Aircraft type:", aircraft_type)
    print("Airports found:", len(result))


    print("\n---- PART 2.3 TEST ----")

    r = [(1,'b1'),(2,'b2'),(3,'b3'),(4,'b4')]
    s = [(1,'c1'),(1,'c2'),(2,'c3'),(3,'c4')]
    t = [(1,'d1'),(2,'d2'),(3,'d3'),(5,'d4')]

    print("Pipelined join:")
    print(pipelined_merge_join(r,s,t))

    print("Three way merge join:")
    print(three_way_sort_merge_join(r,s,t))