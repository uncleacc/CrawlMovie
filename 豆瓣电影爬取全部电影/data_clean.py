import csv
import re
import sys
from datetime import datetime

def clean_movie_data(input_file, output_file):
    """清洗电影数据的主函数"""
    try:
        with open(input_file, 'r', encoding='utf-8-sig') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
            
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            
            # 写入表头
            writer.writeheader()
            
            # 处理每一行数据
            for row in reader:
                cleaned_row = process_movie_row(row)
                writer.writerow(cleaned_row)
                
        print(f"数据清洗完成，已保存到 {output_file}")
        
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"发生未知错误：{e}")
        sys.exit(1)

def process_movie_row(row):
    """处理单行电影数据"""
    # 定义需要清洗的字段及其对应列名映射
    field_mapping = {
        '电影名称': ['电影名称', '名称', 'title'],
        '类型': ['类型', 'genre', 'categories'],
        '导演': ['导演', 'director'],
        '演员': ['演员', '主演', 'cast'],
        '上映时间': ['上映时间', 'release_date', '上映日期'],
        '简介': ['简介', 'summary', 'description'],
        '头图': ['头图', '封面图', 'image']
    }
    
    cleaned_data = {}
    
    # 通过列名映射找到对应的值并清洗
    for cleaned_field, possible_names in field_mapping.items():
        raw_value = find_field_value(row, possible_names)
        if cleaned_field == '上映时间':
            cleaned_data[cleaned_field] = clean_release_date(raw_value)
        elif cleaned_field == '类型' or cleaned_field == '演员' or cleaned_field == '导演':
            cleaned_data[cleaned_field] = process_delimiter_field(raw_value)
        else:
            cleaned_data[cleaned_field] = clean_text(raw_value)
    
    # 保留原始数据中的其他列
    for col_name in row:
        if col_name not in cleaned_data:
            cleaned_data[col_name] = row[col_name]
    
    return cleaned_data

def find_field_value(row, possible_names):
    """在原始数据行中查找可能的列名对应的值"""
    for name in possible_names:
        if name in row:
            return row[name]
    return ''  # 如果找不到匹配的列名，返回空字符串

def clean_text(text):
    """清理文本数据，去除前后空格"""
    try:
        return text.strip() if text else ''
    except AttributeError:
        # 处理非字符串类型
        return str(text).strip() if text is not None else ''

def process_delimiter_field(field_str):
    """处理分隔符字段，将/分隔转换为空格分隔"""
    if not field_str:
        return ''
    
    # 使用/分割字符串
    items = field_str.split('/')
    
    # 去除每个元素的前后空格
    cleaned_items = [item.strip() for item in items]
    
    # 用空格重新连接
    return ' '.join(cleaned_items)

def clean_release_date(date_str):
    """清洗上映日期，转换为YYYY格式"""
    if not date_str:
        return ''
    
    try:
        # 移除所有非数字和横杠的字符
        date_part = re.sub(r'[^\d-]', '', date_str)
        
        # 尝试匹配不同的日期格式
        if not date_part:
            return ''
            
        # 尝试解析常见的日期格式
        for fmt in ('%Y-%m-%d', '%Y%m%d', '%Y/%m/%d', '%Y年%m月%d日'):
            try:
                date_obj = datetime.strptime(date_part[:10], fmt)
                return date_obj.strftime('%Y')
            except ValueError:
                continue
                
        # 尝试解析只有年份的格式
        if len(date_part) == 4 and date_part.isdigit():
            return date_part  # 只返回年份
            
        # 如果无法解析，返回原始的日期部分（前4个字符作为年份）
        return date_part[:4] if date_part else ''
        
    except Exception as e:
        print(f"日期解析错误 ({date_str}): {e}")
        return date_str[:4] if date_str else ''  # 返回前4个字符作为年份备选

if __name__ == "__main__":
    # 默认文件名
    input_file = '豆瓣电影信息.csv'
    output_file = '豆瓣电影信息_清洗版.csv'
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    clean_movie_data(input_file, output_file)