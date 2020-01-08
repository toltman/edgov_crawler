import pandas as pd

df = pd.read_csv('links-1.csv')

print(df.nunique())
