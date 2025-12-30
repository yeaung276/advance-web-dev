import json
import os

# ================= CONFIG =================

DATA_DIR = "./sne-2020-2024"

OUTPUT_SUPERNOVAE = "data/supernova.json"
OUTPUT_SOURCES = "data/sources.json"
OUTPUT_HOSTS = "data/galaxies.json"
OUTPUT_SUBTYPES = "data/subtypes.json"

MAX_TOTAL_RECORDS = 10_000

ATTRIBUTE_KEYS = [
    "lumdist",
    "velocity",
    "redshift",
    "maxabsmag",
    "maxappmag",
]

# ================= GLOBAL STATE =================

total_count = 0

seen_sources = {}
seen_hosts = {}
seen_subtypes = {}

supernova_results = []

# ================= HELPERS =================

def bump(n: int):
    global total_count
    total_count += n
    if total_count > MAX_TOTAL_RECORDS:
        raise RuntimeError(
            f"GLOBAL LIMIT EXCEEDED: {total_count} > {MAX_TOTAL_RECORDS}"
        )


def safe_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def source_key(s):
    return s.get("bibcode") or s.get("doi") or s.get("url")

# ================= MAIN =================
try:
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(DATA_DIR, filename)

        with open(path, "r") as f:
            data = json.load(f)

        # one supernova per file
        sn_name, sn = next(iter(data.items()))

        # ---------- COUNT (FAIL FAST) ----------

        # supernova itself
        bump(1)

        # ---------- SOURCES ----------
        sources = sn.get("sources", [])
        bump(len(sources))

        for s in sources:
            key = source_key(s)
            if key and key not in seen_sources:
                seen_sources[key] = {
                    "name": s.get("name"),
                    "doi": s.get("doi"),
                    "bibcode": s.get("bibcode"),
                    "url": s.get("url"),
                    "secondary": s.get("secondary", False),
                }
                bump(1)  # unique source

        # ---------- SUBTYPES ----------
        subtypes = sn.get("claimedtype", [])
        bump(len(subtypes))

        for t in subtypes:
            key = t.get("value")
            if key and key not in seen_subtypes:
                seen_subtypes[key] = {
                    "name": t.get("value"),
                    "source": t.get("source"),
                }
                bump(1)  # unique subtype

        # ---------- HOST GALAXIES ----------
        hosts = sn.get("host", [])
        bump(len(hosts))

        for h in hosts:
            key = h.get("value")
            if key and key not in seen_hosts:
                seen_hosts[key] = {
                    "name": h.get("value"),
                    "source": h.get("source"),
                }
                bump(1)  # unique host galaxy

        # ---------- ATTRIBUTES ----------
        attribute_count = sum(
            1 for k in ATTRIBUTE_KEYS if k in sn and sn[k]
        )
        bump(attribute_count)

        # ---------- BUILD SUPERNOVA OUTPUT ----------

        supernova_results.append({
            "name": sn_name,
            "sources": [
                {
                    "name": s.get("name"),
                    "doi": s.get("doi"),
                    "secondary": s.get("secondary", False),
                    "url": s.get("url"),
                    "bibcode": s.get("bibcode"),
                    "alias": s.get("alias")
                }
                for s in sources
            ],
            "hostgalaxy": [
                {
                    "name": h.get("value"),
                    "source": h.get("source"),
                }
                for h in hosts
            ],
            "subtype": [
                {
                    "name": t.get("value"),
                    "source": t.get("source"),
                }
                for t in subtypes
            ],
            "attributes": [
                {
                    "name": k,
                    "value": safe_float(sn[k][0].get("value")),
                    "unit": sn[k][0].get("u_value"),
                    "source": sn[k][0].get("source"),
                }
                for k in ATTRIBUTE_KEYS
                if k in sn and sn[k] and safe_float(sn[k][0].get("value")) is not None
            ],
        })

# ================= WRITE OUTPUT FILES =================
finally:
    with open(OUTPUT_SUPERNOVAE, "w") as f:
        json.dump(supernova_results, f, indent=2)

    with open(OUTPUT_SOURCES, "w") as f:
        json.dump(list(seen_sources.values()), f, indent=2)

    with open(OUTPUT_HOSTS, "w") as f:
        json.dump(list(seen_hosts.values()), f, indent=2)

    with open(OUTPUT_SUBTYPES, "w") as f:
        json.dump(list(seen_subtypes.values()), f, indent=2)

# ================= SUMMARY =================

print("DONE")
print(f"Total records counted (including uniques): {total_count}")
print(f"Supernovae: {len(supernova_results)}")
print(f"Unique sources: {len(seen_sources)}")
print(f"Unique host galaxies: {len(seen_hosts)}")
print(f"Unique subtypes: {len(seen_subtypes)}")
