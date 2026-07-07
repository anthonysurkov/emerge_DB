import pandas as pd
import regex

df = pd.read_csv("df_c1.csv", index_col=0)
trgt = regex.compile(r"(GCTG){e<=1}([AG]{3})(GCCG){e<=1}")
varb = regex.compile(r"(TTTCTTTCTTTC){e<=1}.*?([ACGT]{9})(CCCGTTTGCCCG){e<=2}")

for read in df["read"]:
    trgt_m = trgt.search(read)
    varb_m = varb.search(read)
    ts, ti, td = trgt_m.fuzzy_counts
    vs, vi, vd = varb_m.fuzzy_counts

    if ts != 0 or ti != 0 or td != 0:
        print(f"ts {ts}, ti {ti}, td {td}, t: {trgt_m.groups()}")
    if vs != 0 or vi != 0 or vd != 0:
        print(f"vs {vs}, vi {vi}, vd {vd}, v: {varb_m.groups()}")

    if not trgt_m or not varb_m: print(f"fuck. read: {read}")

