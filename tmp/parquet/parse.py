# parquetファイルのパースを行う
import pyarrow.parquet as pq
def parse_parquet(file_path):
    """
    パーケットファイルをパースして、データフレームを返す。

    Args:
        file_path (str): パーケットファイルのパス

    Returns:
        pandas.DataFrame: パーケットファイルの内容を含むデータフレーム
    """
    table = pq.read_table(file_path)
    return table.to_pandas()

if __name__ == "__main__":
    import sys
    import pandas as pd

    if len(sys.argv) != 2:
        print("Usage: python parse.py <parquet_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    df = parse_parquet(file_path)
    print(df.head())  # データフレームの最初の5行を表示
