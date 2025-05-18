import csv
import re
import sys
from datetime import datetime

def clean_movie_data(input_file, output_file):
    """清洗电影数据的主函数"""
    try:
        with open(input_file, 'r', encoding='utf-8-sig') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # 写入表头
            header = next(reader)
            writer.writerow(header)
            
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
    # 确保数据长度正确
    if len(row) < 7:
        row.extend([''] * (7 - len(row)))
    
    cleaned_data = {}
    cleaned_data['电影名称'] = clean_text(row[0])
    cleaned_data['类型'] = clean_text(row[1])
    cleaned_data['导演'] = clean_text(row[2])
    cleaned_data['演员'] = clean_text(row[3])
    cleaned_data['上映时间'] = clean_release_date(row[4])
    cleaned_data['简介'] = clean_text(row[5])
    cleaned_data['头图'] = clean_text(row[6])
    
    return list(cleaned_data.values())

def clean_text(text):
    """清理文本数据，去除前后空格"""
    try:
        return text.strip() if text else ''
    except AttributeError:
        # 处理非字符串类型
        return str(text).strip() if text is not None else ''

def clean_release_date(date_str):
    """清洗上映日期，转换为YYYY-MM-DD格式"""
    if not date_str:
        return ''
    
    try:
        # 移除所有非数字和横杠的字符
        date_part = re.sub(r'[^\d-]', '', date_str)
        
        # 尝试匹配不同的日期格式
        if not date_part:
            return ''
            
        # 尝试解析常见的日期格式
        for fmt in ('%Y-%m-%d', '%Y%m%d'):
            try:
                date_obj = datetime.strptime(date_part[:10], fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        # 如果无法解析，返回原始的日期部分
        return date_part[:10]
        
    except Exception as e:
        print(f"日期解析错误 ({date_str}): {e}")
        return date_str[:10]  # 返回前10个字符作为备选

if __name__ == "__main__":
    # 默认文件名
    input_file = '猫眼电影信息.csv'
    output_file = '猫眼电影信息_清洗版.csv'
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    clean_movie_data(input_file, output_file)    