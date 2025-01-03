import pyarrow.parquet as pq

file_path = "/Users/josh/Desktop/codebase/HomelessDataProject/part-684ff9c123627873.parquet"
table = pq.read_table(file_path)
print(table.to_pandas().head())
