import pandas as pd

infile_manual = "r270xz_chunk_manual.csv"
infile_auto   = "r270xz_chunk_automated.csv"

df_manual = pd.read_csv(infile_manual, index_col=0)
df_auto   = pd.read_csv(infile_auto, index_col=0)

if df_manual.equals(df_auto):
    print("happy!")
else:
    print("sad!")
