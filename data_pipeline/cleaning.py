import pandas as pd


INPUT_FILE = "data_pipeline/outputs/scraped_books.csv"


# --------------------------------
# 1. Load raw scraped data
# --------------------------------

df = pd.read_csv(INPUT_FILE)

print("Raw data loaded successfully.")

print("\nOriginal shape:")
print(df.shape)

print("\nOriginal columns:")
print(df.columns.tolist())


# --------------------------------
# 2. Clean price
# --------------------------------

df["price_gbp"] = (
    df["price"]
    .astype(str)
    .str.replace(r"[^\d.]", "", regex=True)
)

df["price_gbp"] = pd.to_numeric(
    df["price_gbp"],
    errors="coerce"
)


# --------------------------------
# 3. Handle invalid/missing prices
# --------------------------------

missing_prices = df["price_gbp"].isna().sum()

print(
    "\nInvalid/missing prices before imputation:",
    missing_prices
)

if missing_prices > 0:

    price_median = df["price_gbp"].median()

    df["price_gbp"] = df["price_gbp"].fillna(
        price_median
    )

    print(
        "Missing prices replaced with median:",
        price_median
    )


# --------------------------------
# 4. Convert star rating
# --------------------------------

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

df["rating"] = df["star_rating"].map(
    rating_map
)


# --------------------------------
# 5. Handle invalid/missing ratings
# --------------------------------

missing_ratings = df["rating"].isna().sum()

print(
    "\nInvalid/missing ratings before imputation:",
    missing_ratings
)

if missing_ratings > 0:

    rating_median = df["rating"].median()

    df["rating"] = df["rating"].fillna(
        rating_median
    )

    print(
        "Missing ratings replaced with median:",
        rating_median
    )


df["rating"] = (
    df["rating"]
    .round()
    .astype(int)
)


# --------------------------------
# 6. Convert availability
# --------------------------------

df["in_stock"] = (
    df["availability"]
    .astype(str)
    .str.contains(
        "In stock",
        case=False,
        na=False
    )
)


# --------------------------------
# 7. Handle missing title/category
# --------------------------------

rows_before = len(df)

df = df.dropna(
    subset=[
        "title",
        "category"
    ]
)

rows_after = len(df)

print(
    "\nRows dropped because of missing "
    "title/category:",
    rows_before - rows_after
)


# --------------------------------
# 8. Convert GBP to INR
# --------------------------------

GBP_TO_INR = 105.50

df["price_inr"] = (
    df["price_gbp"] * GBP_TO_INR
).round(2)


print("\nCurrency conversion:")
print(
    df[
        [
            "price_gbp",
            "price_inr"
        ]
    ].head()
)


# --------------------------------
# 9. Remove raw columns
# --------------------------------

df = df.drop(
    columns=[
        "price",
        "star_rating",
        "availability"
    ]
)


# --------------------------------
# 10. Final column order
# --------------------------------

df = df[
    [
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category"
    ]
]


# --------------------------------
# 11. Final validation
# --------------------------------

print("\nFinal cleaned data:")
print(df.head())

print("\nFinal columns:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nNumber of rows:")
print(len(df))


# --------------------------------
# 12. Save cleaned data
# --------------------------------

OUTPUT_FILE = (
    "data_pipeline/outputs/cleaned_books.csv"
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    "\nCleaned data saved successfully to:"
)

print(OUTPUT_FILE)