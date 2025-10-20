import pandas as pd

company=["A","B","C"]
df = pd.DataFrame({"A":['A','B','A','A','B'],"B":[11,99,77,88,22],"C":[11,12,15,14,13]})
print(df)
print("*"*40)
df["L"] = pd.cut(df['B'],bins =[0,72,96,120])
print(df)