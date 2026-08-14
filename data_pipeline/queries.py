import sqlite3


DATABASE_FILE = "data_pipeline/books.db"

OUTPUT_FILE = (
    "data_pipeline/outputs/query_outputs.txt"
)

connection = sqlite3.connect(
    DATABASE_FILE
)

queries = {

    "Query 1 - SELECT WHERE": """
        SELECT
            title,
            rating,
            price_gbp
        FROM books
        WHERE rating >= 4;
    """,

    "Query 2 - ORDER BY": """
        SELECT
            title,
            price_gbp,
            price_inr
        FROM books
        ORDER BY price_gbp DESC;
    """,

    "Query 3 - LIMIT": """
        SELECT
            title,
            price_gbp,
            rating
        FROM books
        ORDER BY price_gbp DESC
        LIMIT 10;
    """,

    "Query 4 - DISTINCT": """
        SELECT DISTINCT
            rating
        FROM books
        ORDER BY rating;
    """,

    "Query 5 - BETWEEN": """
        SELECT
            title,
            price_gbp,
            rating
        FROM books
        WHERE price_gbp BETWEEN 20 AND 40
        ORDER BY price_gbp;
    """,

    "Query 6 - JOIN": """
        SELECT
            b.title,
            c.category_name,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id;
    """
}

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as output_file:

    for query_name, query in queries.items():

        print("\n================================")
        print(query_name)
        print("================================")

        print("SQL:")
        print(query.strip())

        output_file.write(
            "\n================================\n"
        )

        output_file.write(
            f"{query_name}\n"
        )

        output_file.write(
            "================================\n"
        )

        output_file.write(
            "\nSQL:\n"
        )

        output_file.write(
            query.strip()
        )

        output_file.write(
            "\n\nOUTPUT:\n"
        )

        cursor = connection.execute(
            query
        )

        rows = cursor.fetchall()

        for row in rows:

            print(row)

            output_file.write(
                str(row) + "\n"
            )


connection.close()

print(
    "\nAll SQL queries executed successfully."
)

print(
    "Query outputs saved to:"
)

print(OUTPUT_FILE)