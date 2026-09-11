import sqlite3
import pandas as pd


DATABASE = "data_pipeline/zepto_books.db"


def compare_sql_and_pandas():

    conn = sqlite3.connect(DATABASE)

    # Read books table
    books_df = pd.read_sql(
        "SELECT * FROM books",
        conn
    )

    # Read categories table
    categories_df = pd.read_sql(
        "SELECT * FROM categories",
        conn
    )

    # SQL JOIN
    sql_query = """
    SELECT
        b.title,
        b.price_gbp,
        b.price_inr,
        b.rating,
        b.in_stock,
        c.category_name
    FROM books b
    JOIN categories c
        ON b.category_id = c.category_id
    ORDER BY b.rating DESC, b.title ASC
    LIMIT 10;
    """

    sql_result = pd.read_sql(
        sql_query,
        conn
    )

    # Pandas merge
    pandas_result = pd.merge(
        books_df,
        categories_df,
        on="category_id",
        how="inner"
    )

    # Select the same columns
    pandas_result = pandas_result[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category_name"
        ]
    ]

    # Same sorting and limit as SQL
    pandas_result = pandas_result.sort_values(
    by=["rating", "title"],
    ascending=[False, True]
    ).head(10)

    # Reset indexes
    sql_result = sql_result.reset_index(drop=True)

    pandas_result = pandas_result.reset_index(drop=True)

    # Display results
    print("\nSQL JOIN RESULT")
    print(sql_result)

    print("\nPANDAS MERGE RESULT")
    print(pandas_result)

    # Compare results
    print("\nDo SQL JOIN and Pandas merge() match?")

    print(
        sql_result.equals(pandas_result)
    )

    conn.close()


if __name__ == "__main__":
    compare_sql_and_pandas()