import pandas as pd
import json

# 读取文件并添加数据源标记
df1 = pd.read_csv('爬取猫眼电影数据/猫眼电影信息_清洗版.csv')
df1['数据源'] = '猫眼'  # 标记数据源
df2 = pd.read_csv('豆瓣电影爬取全部电影/豆瓣电影信息_清洗版.csv')
df2['数据源'] = '豆瓣'  # 标记数据源

# 去除电影名称空格
df1['电影名称'] = df1['电影名称'].str.strip()
df2['电影名称'] = df2['电影名称'].str.strip()

# 统计同名电影数量
common_movies = set(df1['电影名称']) & set(df2['电影名称'])
print(f"同名电影数量: {len(common_movies)}")

# 为同名电影添加合并标记
df1['合并标记'] = df1['电影名称'].isin(common_movies).astype(int)
df2['合并标记'] = df2['电影名称'].isin(common_movies).astype(int)

# 合并数据（优先保留猫眼数据）
df_all = pd.concat([df1, df2], ignore_index=True)

# **关键检查：打印合并后的列名**
print("合并后的列名：", df_all.columns)  # 确保包含'数据源'和'电影名称'

# 过滤无效列（仅排除Unnamed开头的列，保留数据源）
df_all = df_all[[col for col in df_all.columns if not col.startswith('Unnamed:')]]

# 分组合并函数
def merge_group(group):
    # 合并数据源（处理可能的缺失值）
    if '数据源' not in group.columns:
        raise ValueError("'数据源'列不存在")
    
    # 获取所有数据源
    sources = sorted(set(group['数据源'].dropna()))
    
    # 检查是否有猫眼数据
    has_maoyan = any('猫眼' in s for s in sources)
    
    # 如果有猫眼数据，优先使用猫眼数据行
    if has_maoyan:
        cat_data = group[group['数据源'] == '猫眼']
        if not cat_data.empty:
            merged = cat_data.iloc[0].copy()
        else:
            merged = group.iloc[0].copy()  # 安全备份
    else:
        merged = group.iloc[0].copy()
    
    # 合并数据源标记
    merged['数据源'] = ' '.join(sources) if sources else '未知'
    
    # 合并标记处理
    if '合并标记' in merged:
        merged['合并标记'] = group['合并标记'].max()
    
    return merged

# 执行分组聚合
df_merged = df_all.groupby('电影名称', as_index=False).apply(merge_group).reset_index(drop=True)

# 保存为JSON
with open('合并后的电影信息.json', 'w', encoding='utf-8') as f:
    json.dump(df_merged.to_dict('records'), f, ensure_ascii=False, indent=4)

print("合并完成，结果已保存。")

# 打印合并电影的统计信息
merged_count = df_merged['合并标记'].sum()
print(f"实际合并的电影数量: {merged_count}")