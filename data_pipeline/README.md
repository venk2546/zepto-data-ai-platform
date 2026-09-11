# Zepto Data AI Platform - Data Pipeline

## 1. Project Overview

This project demonstrates a complete data pipeline for collecting,
cleaning, storing, and querying book data.

The project uses Python, Requests, BeautifulSoup, Pandas, SQLite,
and SQL.

## 2. Selected Book Categories

The project uses the following three categories:

- Travel
- Mystery
- Historical Fiction

A total of 69 books were collected from these three categories.

## 3. Data Source

The book data was collected from:

Books to Scrape

Website:
http://books.toscrape.com/

## 4. Data Pipeline

The complete pipeline is:

Scraping
    ↓
raw_books.csv
    ↓
Data Cleaning
    ↓
cleaned_books.csv
    ↓
SQLite Database
    ↓
SQL Queries
    ↓
Pandas merge()

## 5. Project Files

### scraper.py

Collects book information from the selected categories.

The scraper collects:

- title
- price
- rating
- availability
- category

Output:

raw_books.csv

### clean_data.py

Cleans the scraped book data and prepares it for database storage.

Output:

cleaned_books.csv

### database.py

Creates the SQLite database and stores the cleaned data.

Database:

zepto_books.db

Tables:

- books
- categories

### queries.py

Runs SQL queries on the SQLite database.

The queries demonstrate:

- SELECT
- WHERE
- ORDER BY
- LIMIT
- DISTINCT
- BETWEEN
- IN
- JOIN

### pandas_comparison.py

Loads the SQLite tables into Pandas DataFrames.

It demonstrates `pandas.merge()` by combining:

- books
- categories

using the common column:

category_id

The Pandas merge result is compared with the SQL JOIN result.

The comparison returned:

True

## 6. SQL JOIN

The SQL JOIN combines the books and categories tables.

Example:

```sql
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

The equivalent Pandas operation is:
pd.merge(
    books_df,
    categories_df,
    on="category_id",
    how="inner"
)
The SQL JOIN and Pandas merge() produce equivalent results.

The comparison returned:

True

How to Run the Project
=======================

Open the project in VS Code.

Make sure the virtual environment is activated.

Install the required packages: pip install -r requirements.txt
Run the scraper:python data_pipeline/scraper.py
Run the data cleaning script:python data_pipeline/clean_data.py
Create the SQLite database:python data_pipeline/database.py
Run the SQL queries:python data_pipeline/queries.py
Run the Pandas merge comparison:python data_pipeline/pandas_comparison.py