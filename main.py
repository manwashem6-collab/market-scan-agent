import pandas as pd

data = [
    {"Product": "Cement 50kg", "Supplier": "Basco", "Price": 720},
    {"Product": "Paint 4L", "Supplier": "Crown", "Price": 1350},
    {"Product": "Tiles 30x30", "Supplier": "Tile World", "Price": 950},
]

pd.DataFrame(data).to_csv("output.csv", index=False)
print("main.py produced output.csv")
