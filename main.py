import pandas as pd

# Example dataset (you'll replace this with real data later)
data = [
    {"Product": "Cement 50kg", "Supplier": "Basco", "Price": 720},
    {"Product": "Paint 4L", "Supplier": "Crown", "Price": 1350},
    {"Product": "Tiles 30x30", "Supplier": "Tile World", "Price": 950},
]

df = pd.DataFrame(data)

# Save the dataset as CSV so the GitHub Action can convert it to Excel
df.to_csv("output.csv", index=False)

print("✅ Market scan data generated successfully.")
