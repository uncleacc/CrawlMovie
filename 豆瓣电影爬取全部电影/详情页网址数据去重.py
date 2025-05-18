import pandas as pd
from openpyxl  import load_workbook
df = pd.read_excel('详情页网址.xlsx', sheet_name='详情页网址')
#df = pd.read_excel('详情页址.xls', sheet_name='详情页网址')
df = df.drop_duplicates()   #删除重复项
df.to_excel('详情页网址_去重后.xlsx', sheet_name='详情页网址',index=False)
#df_1 = pd.read_excel('详情页网址_去重后.xlsx', sheet_name='详情页网址')