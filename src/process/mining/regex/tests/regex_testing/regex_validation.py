import pandas as pd

df_val = pd.read_csv('r270x_z_regex_validation.csv', index_col=0)
df_r = pd.read_csv('r270x_z_regex_chunk.csv')
df_c = pd.read_csv('r270x_z_casey_chunk.csv')
print(f'len df_r: {df_r.shape[0]}')
print(f'len df_c: {df_c.shape[0]}')

coding_cols = ['AAA', 'AAG', 'AGA', 'GAA', 'GGA']
df_r['5to3'] = df_r['n10']
df_r['n'] = df_r[coding_cols].sum(axis=1)
df_r['k'] = df_r['GAA']
df_r = df_r[['5to3', 'n', 'k']]
df_c['5to3'] = df_c.iloc[:,0]
df_c['n'] = df_c[coding_cols].sum(axis=1)
df_c['k'] = df_c['GAA']
df_c = df_c[['5to3', 'n', 'k']]

df_val_adjunct = df_val.loc[df_val.isna().any(axis=1)]
df_val = df_val.dropna()

df_val_r = pd.merge(df_val, df_r, how='outer', on='5to3')
df_val_c = pd.merge(df_val, df_c, how='outer', on='5to3')
cols = [c for c in df_val_r.columns if c != 'comment'] + ['comment']
df_val_r = df_val_r[cols].dropna(subset=['comment']) # data currently generated
df_val_c = df_val_c[cols].dropna(subset=['comment']) # with a larger dataset
                                                     # than what was manually
                                                     # labeled
print(f'len df_val_r: {df_val_r.shape[0]}')
print(f'len df_val_c: {df_val_c.shape[0]}')

df_val_r['agree'] = (
    (df_val_r['n'] > 0) & (df_val_r['valid_manual'] > 0)
    | (pd.isna(df_val_r['n'])) & (df_val_r['valid_manual'] == 0)
)
df_val_c['agree'] = (
    (df_val_c['n'] > 0) & (df_val_c['valid_manual'] > 0)
    | (pd.isna(df_val_c['n'])) & (df_val_c['valid_manual'] == 0)
)

df_val_r_disagree = df_val_r[df_val_r['agree'] == False]
df_val_c_disagree = df_val_c[df_val_c['agree'] == False]
df_val_r_agree = df_val_r[df_val_r['agree'] == True]
df_val_c_agree = df_val_c[df_val_c['agree'] == True]

print(f'len df_val_r_disagree: {df_val_r_disagree.shape[0]}')
print(f'len df_val_c_disagree: {df_val_c_disagree.shape[0]}')
print(f'len df_val_r_agree: {df_val_r_agree.shape[0]}')
print(f'len df_val_c_agree: {df_val_c_agree.shape[0]}')
print(f'df_val_r agree rate: {df_val_r["agree"].sum() / df_val_r.shape[0]}')
print(f'df_val_c agree rate: {df_val_c["agree"].sum() / df_val_c.shape[0]}')

print('df_val_r.head():')
print(df_val_r.head())
print('df_val_c.head():')
print(df_val_c.head())

print('df_val_r_disagree:')
print(df_val_r_disagree.to_string())
print('df_val_c_disagree:')
print(df_val_c_disagree.to_string())
