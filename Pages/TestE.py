import pandas as pd
from longsea import al2

sample_data = {
    'A': [1, 2, 3, 4, 5],
    'B': [1,3, 7, 2,4],
    'C': [11, 12, 33, 14, 25],
    'D': [14, 22, 17, 31, 15],}

df = pd.DataFrame(sample_data)
print("原始 DataFrame:")
print(df)

print("测试1")
df_with_ranks_by_name = al2.df_add_rank(df, lst=[2, 4], direction='last')
print(df_with_ranks_by_name)











