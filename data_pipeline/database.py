import sqlite3
import pandas as pd

DATABASE_FILE = "data_pipeline/books.db"

INPUT_FILE = (
    "data_pipeline/outputs/cleaned_books.csv"
)


df = pd.read_csv(INPUT_FILE)

print("Cleaned data loaded successfully.")

print("\nNumber of books:")
print(len(df))

print("\nNumber of categories:")
print(df["category"].nunique())

connection = sqlite3.connect(
    DATABASE_FILE
)

cursor = connection.cursor()

print("\nDatabase connection successful.")


connection.execute(
    "PRAGMA foreign_keys = ON"
)


cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (

        category_id INTEGER PRIMARY KEY AUTOINCREMENT,

        category_name TEXT UNIQUE NOT NULL

    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (

        book_id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT NOT NULL,

        price_gbp REAL NOT NULL,

        price_inr REAL NOT NULL,

        rating INTEGER NOT NULL,

        in_stock INTEGER NOT NULL,

        category_id INTEGER NOT NULL,

        FOREIGN KEY (category_id)
            REFERENCES categories(category_id)

    )
""")


connection.commit()

print("\nTables created successfully.")

categories = (
    df["category"]
    .dropna()
    .unique()
)

for category in categories:

    cursor.execute(
        """
        INSERT OR IGNORE INTO categories
        (category_name)
        VALUES (?)
        """,
        (category,)
    )


connection.commit()

print(
    "Categories inserted successfully."
)


cursor.execute("""
    SELECT
        category_id,
        category_name
    FROM categories
    ORDER BY category_id
""")

category_rows = cursor.fetchall()


print("\nCategories in database:")

for row in category_rows:

    print(
        row[0],
        "|",
        row[1]
    )


cursor.execute("""
    SELECT
        category_id,
        category_name
    FROM categories
""")

category_mapping = {
    category_name: category_id
    for category_id, category_name
    in cursor.fetchall()
}


print("\nCategory mapping:")
print(category_mapping)


for _, row in df.iterrows():

    category_id = category_mapping[
        row["category"]
    ]

    cursor.execute(
        """
        INSERT INTO books (
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            row["title"],
            row["price_gbp"],
            row["price_inr"],
            row["rating"],
            int(row["in_stock"]),
            category_id
        )
    )


connection.commit()

print(
    "\nBooks inserted successfully."
)


cursor.execute("""
    SELECT COUNT(*)
    FROM books
""")

book_count = cursor.fetchone()[0]

print(
    "\nBooks in database:",
    book_count
)

cursor.execute("""
    SELECT
        book_id,
        title,
        price_gbp,
        price_inr,
        rating,
        in_stock,
        category_id
    FROM books
    LIMIT 5
""")

book_rows = cursor.fetchall()

print("\nFirst 5 books in database:")

for row in book_rows:

    print(row)

connection.close()

print("\nDatabase connection closed.")