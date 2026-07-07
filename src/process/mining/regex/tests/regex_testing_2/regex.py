import pandas as pd
import regex

indir = "data"
infile = "small_r270x_chunk.csv"

max_dist = 7

tplt = r"(CCTCTCCCAAGTCCACACAGAACGGGGCTGAAAGCCGGGTTTCTTTCTTTC"
tplt += r"CCGNNNNNNNNNCCCGTTTGCCCGTAGAGTCGCTGTTC)"

tplt = tplt.replace("U", "T")
tplt = tplt.replace("A", "[AG]")
tplt = tplt.replace("N", "[ACGT]")
tplt = tplt + "{e<=" + str(max_dist) + "}"
pattern = regex.compile(tplt, regex.BESTMATCH)

trgt = regex.compile(r"(?:GCTG){e<=1}([AG]{3})(?:GCCG){e<=1}")
varb = regex.compile(r"(?:TTTCTTTCTTTC){e<=1}.*?([ACGT]{9})(?:CCCGTTTGCCCG){e<=2}")

df = pd.read_csv(f"{indir}/{infile}")
df = df.rename(columns={"as.character(sread(chunk))": "seq"})

def find_match(seq):
    m = pattern.search(seq)
    if not m:
        return None, None

    read = m.group()
    print(read)
    target_m = trgt.search(read)
    if not target_m:
        print("b")
        return None, None
    n10_m = varb.search(read)
    if not n10_m:
        print("c")
        return None, None

    target_seq = target_m.group(1)
    n10_seq = n10_m.group(1)
    return n10_seq, target_seq

records = []
for s in df["seq"]:
    n10, target = find_match(s)
    if n10 is None or target is None:
        continue
    records.append({"n10": n10, "target": target})

table = pd.DataFrame(records)
if table.empty:
    print("No matches found")
else:
    ctab = pd.crosstab(table["n10"], table["target"]).astype(int)
    tot = ctab.sum().sum()
    print(ctab.to_string())
    print(f"Number of n10s: {ctab.shape[0]}")
    print(f"Number of reads: {tot}")
