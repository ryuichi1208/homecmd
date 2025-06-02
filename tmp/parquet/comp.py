import polars as pl
import numpy as np
import time
from datetime import datetime, timedelta

# ランダムデータの生成
n_rows = 100_000_000

# 日付データの生成
# 2024年1月1日からn秒後の日付
start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(seconds=x) for x in range(n_rows)]

# データフレームの作成
df = pl.DataFrame({
    # 連番のID
    "id": range(n_rows),
    # タイムスタンプ
    "date": dates,
    # 0から1000の一様分布からのランダム値
    "value": np.random.uniform(0, 1000, n_rows),
    # A,B,C,Dからランダムに選択されたカテゴリ
    "category": np.random.choice(["A", "B", "C", "D"], n_rows),
    # TrueとFalseからランダムに選択されたフラグ
    "flag": np.random.choice([True, False], n_rows)
})

# 圧縮形式を分けて保存
# 各圧縮形式での書き込み時間を計測
results = {c: [] for c in ["zstd", "lz4", "snappy"]}

for compression in ["zstd", "lz4", "snappy"]:
    print(f"\n{compression}での書き込み:")
    for i in range(5):
        start = time.time()
        df.write_parquet(
            f"test_data_{compression}.parquet",
            compression=compression,
        )
        end = time.time()
        elapsed = end - start
        results[compression].append(elapsed)
        print(f"  実行 {i+1}: {elapsed:.2f}秒")
    
    avg_time = sum(results[compression]) / len(results[compression])
    print(f"{compression}の平均書き込み時間: {avg_time:.2f}秒")

print("データセットを生成しました。行数:", n_rows)
