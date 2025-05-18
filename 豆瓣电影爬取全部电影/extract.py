import pandas as pd
import os


def extract_rows():
    """从当前目录下的 input.xlsx 中提取第 11000 到 13000 行数据"""
    input_file = "详情页网址_去重后.xlsx"
    output_file = "中国电影信息.csv"

    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_file):
            print(f"错误：找不到输入文件 {input_file}")
            return False

        # 获取文件绝对路径用于显示
        input_abs_path = os.path.abspath(input_file)
        output_abs_path = os.path.abspath(output_file)

        # 读取 Excel 文件
        print(f"正在读取文件: {input_abs_path}")
        df = pd.read_excel(input_file)

        # 检查数据行数是否足够
        total_rows = len(df)
        if total_rows < 11000:
            print(f"错误：文件中只有 {total_rows} 行数据，不足 11000 行。")
            return False

        # 提取指定行 (注意行索引从 0 开始)
        start_row = 10999  # 第 11000 行的索引是 10999
        end_row = 12999  # 第 13000 行的索引是 12999
        extracted_df = df.iloc[start_row:end_row + 1]

        # 保存提取的数据到新 Excel 文件
        extracted_df.to_csv(output_file, index=False)
        print(f"成功提取 {len(extracted_df)} 行数据到 {output_abs_path}")
        return True

    except Exception as e:
        print(f"发生未知错误: {e}")
        return False


if __name__ == "__main__":
    success = extract_rows()
    exit(0 if success else 1)