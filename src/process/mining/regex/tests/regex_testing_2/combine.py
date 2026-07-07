import pandas as pd

seqs1 = [
    "TCTTCTTGC",
    "TCTTGTTGC",
    "TCTTATTGC",
    "TCTTTTTGC"
]
seqs2 = [
    "CCTTCTTGA",
    "CCTTGTTGA",
    "CCTTATTGA",
    "CCTTTTTGA"
]
seqs3 = [
    "ACCTCTTGA",
    "ACCTGTTGA",
    "ACCTCTTGA",
    "ACCTTTTGA"
]

df_r = pd.read_csv("r270x_regex_reads_peteseqs.csv")
df_c = pd.read_csv("r270x_casey_reads_peteseqs.csv")

df_r1 = df_r[df_r["n10"].isin(seqs1)]
df_r2 = df_r[df_r["n10"].isin(seqs2)]
df_r3 = df_r[df_r["n10"].isin(seqs3)]
df_r1 = df_r1[["n10", "target", "seq"]].reset_index(drop=True)
df_r2 = df_r2[["n10", "target", "seq"]].reset_index(drop=True)
df_r3 = df_r3[["n10", "target", "seq"]].reset_index(drop=True)

df_c1 = df_c[df_c["n10"].isin(seqs1)]
df_c2 = df_c[df_c["n10"].isin(seqs2)]
df_c3 = df_c[df_c["n10"].isin(seqs3)]
df_c1 = df_c1[["n10", "codon", "read"]].reset_index(drop=True)
df_c2 = df_c2[["n10", "codon", "read"]].reset_index(drop=True)
df_c3 = df_c3[["n10", "codon", "read"]].reset_index(drop=True)

df_r1.to_csv("df_r1.csv")
df_r2.to_csv("df_r2.csv")
df_r3.to_csv("df_r3.csv")
df_c1.to_csv("df_c1.csv")
df_c2.to_csv("df_c2.csv")
df_c3.to_csv("df_c3.csv")
