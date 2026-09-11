import sqlite3
import pandas as pd


DATABASE = "data_pipeline/zepto_books.db"


def run_queries():

    conn = sqlite3.connect(DATABASE)

    # Query 1: SELECT + WHERE
    query1 = """
    SELECT title, price_gbp, rating
    FROM books
    WHERE rating >= 4;
    """

    print("\nQUERY 1 - SELECT + WHERE")
    print(pd.read_sql(query1, conn))

    # Query 2: ORDER BY + LIMIT
    query2 = """
    SELECT title, price_gbp, rating
    FROM books
    ORDER BY price_gbp DESC
    LIMIT 10;
    """

    print("\nQUERY 2 - ORDER BY + LIMIT")
    print(pd.read_sql(query2, conn))

    # Query 3: DISTINCT
    query3 = """
    SELECT DISTINCT category_name
    FROM categories;
    """

    print("\nQUERY 3 - DISTINCT")
    print(pd.read_sql(query3, conn))

    # Query 4: BETWEEN
    query4 = """
    SELECT title, price_gbp
    FROM books
    WHERE price_gbp BETWEEN 20 AND 40;
    """

    print("\nQUERY 4 - BETWEEN")
    print(pd.read_sql(query4, conn))

    # Query 5: IN
    query5 = """
    SELECT title, category_id, rating
    FROM books
    WHERE category_id IN (1, 2);
    """

    print("\nQUERY 5 - IN")
    print(pd.read_sql(query5, conn))

    # Query 6: JOIN
    query6 = """
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
    ORDER BY b.rating DESC
    LIMIT 10;
    """

    print("\nQUERY 6 - JOIN")

    join_result = pd.read_sql(
        query6,
        conn
    )

    print(join_result)

    conn.close()


if __name__ == "__main__":
    run_queries()