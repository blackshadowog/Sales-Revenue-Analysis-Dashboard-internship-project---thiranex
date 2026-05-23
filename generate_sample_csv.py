"""
Generate a sample_sales_data.csv file for testing the dashboard import feature.
Run: python generate_sample_csv.py
"""
import pandas as pd
import numpy as np

def generate_and_save():
    np.random.seed(99)
    products   = ["Laptop Pro","Smart Watch","Wireless Earbuds","Tablet Ultra",
                  "Gaming Mouse","Mechanical Keyboard","4K Monitor","USB-C Hub","Webcam HD","SSD Drive"]
    categories = ["Electronics","Wearables","Audio","Electronics","Peripherals",
                  "Peripherals","Displays","Accessories","Peripherals","Storage"]
    regions    = ["North","South","East","West","Central"]
    persons    = ["Alice Johnson","Bob Smith","Carol White","David Brown",
                  "Emma Davis","Frank Miller","Grace Wilson","Henry Moore"]

    dates = pd.date_range("2023-01-01","2024-12-31",freq="D")
    n = 1000
    price_map = dict(zip(products,[1299,349,179,899,79,149,499,59,99,129]))
    cat_map   = dict(zip(products, categories))

    df = pd.DataFrame({
        "Date":        np.random.choice(dates,n),
        "Product":     np.random.choice(products,n),
        "Region":      np.random.choice(regions,n),
        "SalesPerson": np.random.choice(persons,n),
        "Units":       np.random.randint(1,20,n),
        "Discount":    np.random.choice([0,0.05,0.10,0.15],n,p=[.5,.2,.2,.1]),
    })
    df["Category"]     = df["Product"].map(cat_map)
    df["UnitPrice"]    = df["Product"].map(price_map)
    df["Revenue"]      = (df["Units"] * df["UnitPrice"] * (1-df["Discount"])).round(2)
    df["COGS"]         = (df["Revenue"] * np.random.uniform(0.45,0.65,n)).round(2)
    df["Profit"]       = (df["Revenue"] - df["COGS"]).round(2)
    df["ProfitMargin"] = ((df["Profit"]/df["Revenue"])*100).round(1)
    df = df.sort_values("Date").reset_index(drop=True)

    df.to_csv("sample_sales_data.csv", index=False)
    print(f"✅  Saved sample_sales_data.csv  ({len(df):,} rows)")
    print(df.head())

if __name__ == "__main__":
    generate_and_save()
