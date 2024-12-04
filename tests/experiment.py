import pandas as pd


expected_data = pd.DataFrame({
    "id": [1, 2],
    "name": ["Inception", "Pride and Prejudice"],
    "year_released": [2010, 2006],
    "status": ["Want to watch", "Watched"],
    "rating": [None, 5]
})


def df_pretty_print(df):
    dtype_mapping = {
        'int64': 'int',
        'float64': 'float',
        'object': 'str'
    }
    rows = [
        f"{col} ({dtype_mapping.get(str(dtype), dtype)}): {list(df[col])}"
        for col, dtype in zip(df.columns, df.dtypes)
    ]
    return "\n".join(rows)

print(df_pretty_print(expected_data))