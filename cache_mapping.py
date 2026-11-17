"""
Question 2 : Cache Mapping Simulation
Compares Direct-Mapped, 2-Way Set-Associative and Fully Associative caches.

Model
-----
* The cache has `blocks` lines. Each request is a memory block number.
* One engine simulates all three mappings. Only the number of ways differs:
      Direct-Mapped     -> ways = 1,       sets = blocks
      Set-Associative   -> ways = 2,       sets = blocks / 2
      Fully Associative -> ways = blocks,  sets = 1
* Placement rule : set = block mod sets
* Replacement    : LRU inside the chosen set

Run:  python3 cache_mapping.py                 (0 4 8 0 4 12, 4 blocks)
      python3 cache_mapping.py 8 0 1 2 3 0 1   (8 blocks, custom trace)
"""
import sys


class Cache:
    def __init__(self, blocks, ways):
        self.ways = ways
        self.sets = blocks // ways
        # each line: [block number or None, last-used time]
        self.lines = [[[None, 0] for _ in range(ways)] for _ in range(self.sets)]
        self.clock = 0

    def access(self, block):
        self.clock += 1
        s = block % self.sets
        row = self.lines[s]
        for w, line in enumerate(row):               # search the set
            if line[0] == block:
                line[1] = self.clock                 # refresh LRU time
                return True, s, w, None
        for w, line in enumerate(row):               # free line first
            if line[0] is None:
                row[w] = [block, self.clock]
                return False, s, w, None
        w = min(range(self.ways), key=lambda i: row[i][1])   # LRU victim
        victim = row[w][0]
        row[w] = [block, self.clock]
        return False, s, w, victim

    def snapshot(self):
        return " ".join(
            "S%d[%s]" % (i, " ".join("-" if l[0] is None else str(l[0]) for l in row))
            for i, row in enumerate(self.lines))


def run(title, blocks, ways, trace):
    c = Cache(blocks, ways)
    print("\n" + "-" * 78)
    print("%s  (%d sets x %d ways, set = block mod %d)" % (title, c.sets, c.ways, c.sets))
    print("-" * 78)
    print("%-3s %-8s %-5s %-5s %-6s %-8s %s" % ("#", "Block", "Set", "Way", "Result", "Evicted", "Cache after access"))
    hits = evictions = 0
    for i, b in enumerate(trace, 1):
        hit, s, w, v = c.access(b)
        hits += hit
        evictions += v is not None
        print("%-3d %-8d S%-4d W%-4d %-6s %-8s %s" % (
            i, b, s, w, "HIT" if hit else "MISS", "-" if v is None else v, c.snapshot()))
    n = len(trace)
    print("-" * 78)
    print("Hits = %d  Misses = %d  Hit rate = %.2f%%  Miss rate = %.2f%%  Evictions = %d" % (
        hits, n - hits, 100 * hits / n, 100 * (n - hits) / n, evictions))
    return dict(name=title, layout="%d x %d" % (c.sets, c.ways), hits=hits, misses=n - hits, ev=evictions)


def main():
    blocks, trace = 4, [0, 4, 8, 0, 4, 12]
    if len(sys.argv) > 2:
        blocks, trace = int(sys.argv[1]), [int(x) for x in sys.argv[2:]]
    print("=" * 78)
    print("CACHE MAPPING SIMULATION   cache blocks = %d   requests = %s" % (blocks, trace))
    print("=" * 78)
    res = [run("DIRECT-MAPPED", blocks, 1, trace),
           run("2-WAY SET-ASSOCIATIVE", blocks, 2, trace),
           run("FULLY ASSOCIATIVE", blocks, blocks, trace)]
    n = len(trace)
    print("\n" + "=" * 78)
    print("COMPARISON (%d requests)" % n)
    print("=" * 78)
    print("%-24s %-8s %-5s %-7s %-9s %-10s %s" % ("Technique", "SetsxWay", "Hits", "Misses", "Hit rate", "Miss rate", "Evictions"))
    for r in res:
        print("%-24s %-8s %-5d %-7d %-9s %-10s %d" % (
            r["name"], r["layout"], r["hits"], r["misses"],
            "%.2f%%" % (100 * r["hits"] / n), "%.2f%%" % (100 * r["misses"] / n), r["ev"]))
    best = max(res, key=lambda r: (r["hits"], -r["ev"]))
    print("Best for this trace: %s (%d hits)" % (best["name"], best["hits"]))


main()
