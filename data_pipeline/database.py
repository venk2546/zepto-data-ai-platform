import sqlite3
import pandas as pd


DATABASE = "data_pipeline/zepto_books.db"


def create_database():

    # Load cleaned data
    df = pd.read_csv(
        "data_pipeline/cleaned_books.csv"
    )

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    # Enable foreign key support
    cursor.execute(
        "PRAGMA foreign_keys = ON"
    )

    # Drop existing tables
    cursor.execute(
        "DROP TABLE IF EXISTS books"
    )

    cursor.execute(
        "DROP TABLE IF EXISTS categories"
    )

    # Create categories table
    cursor.execute("""
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT UNIQUE NOT NULL
        )
    """)

    # Create books table
    cursor.execute("""
        CREATE TABLE books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL,
            price_inr REAL,
            rating INTEGER,
            in_stock INTEGER,
            category_id INTEGER,
            FOREIGN KEY (category_id)
                REFERENCES categories(category_id)
        )
    """)

    # Insert categories
    categories = sorted(
        df["category"].unique()
    )

    for category in categories:

        cursor.execute(
            """
            INSERT INTO categories(category_name)
            VALUES (?)
            """,
            (category,)
        )

    # Insert books
    for _, row in df.iterrows():

        cursor.execute(
            """
            SELECT category_id
            FROM categories
            WHERE category_name = ?
            """,
            (row["category"],)
        )

        category_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO books
            (
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

    conn.commit()

    print("Database created successfully.")

    # Check number of records
    book_count = cursor.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    category_count = cursor.execute(
        "SELECT COUNT(*) FROM categories"
    ).fetchone()[0]

    print("Books:", book_count)
    print("Categories:", category_count)

    conn.close()


if __name__ == "__main__":
    create_database()
