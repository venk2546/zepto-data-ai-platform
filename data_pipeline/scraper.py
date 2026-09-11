import requests
from bs4 import BeautifulSoup
import pandas as pd


BASE_URL = "http://books.toscrape.com/"

CATEGORIES = [
    "Travel",
    "Mystery",
    "Historical Fiction"
]


def get_soup(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")


def get_category_urls():
    soup = get_soup(BASE_URL)

    category_urls = {}

    for link in soup.select("div.side_categories ul li ul li a"):

        category_name = link.get_text(strip=True)

        if category_name in CATEGORIES:

            category_url = BASE_URL + link["href"]

            category_urls[category_name] = category_url

    return category_urls


def scrape_category(category_name, category_url):

    books = []

    next_page_url = category_url

    while next_page_url:

        print(f"Scraping: {category_name} -> {next_page_url}")

        soup = get_soup(next_page_url)

        book_items = soup.select("article.product_pod")

        for book in book_items:

            title_element = book.select_one("h3 a")

            if title_element:
                title = title_element.get("title")
            else:
                title = None

            price_element = book.select_one(".price_color")

            if price_element:
                price = price_element.get_text(strip=True)
            else:
                price = None

            rating_element = book.select_one("p.star-rating")

            if rating_element:

                rating_classes = rating_element.get("class", [])

                star_rating = None

                for rating in ["One", "Two", "Three", "Four", "Five"]:

                    if rating in rating_classes:
                        star_rating = rating
                        break

            else:
                star_rating = None

            availability_element = book.select_one(".availability")

            if availability_element:

                availability = availability_element.get_text(
                    " ",
                    strip=True
                )

            else:
                availability = None

            books.append({
                "title": title,
                "price": price,
                "star_rating": star_rating,
                "availability": availability,
                "category": category_name
            })

        next_link = soup.select_one("li.next a")

        if next_link:

            next_page_url = (
                category_url.rsplit("/", 1)[0]
                + "/"
                + next_link["href"]
            )

        else:

            next_page_url = None

    return books


def main():

    print("Finding selected categories...")

    category_urls = get_category_urls()

    print("\nSelected categories found:")

    for category, url in category_urls.items():

        print(f"{category}: {url}")

    all_books = []

    for category in CATEGORIES:

        if category not in category_urls:

            print(
                f"WARNING: Category not found: {category}"
            )

            continue

        books = scrape_category(
            category,
            category_urls[category]
        )

        all_books.extend(books)

        print(
            f"{category}: {len(books)} books scraped"
        )

    df = pd.DataFrame(all_books)

    print("\n-----------------------------")
    print("SCRAPING COMPLETE")
    print("-----------------------------")

    print(
        "Total books:",
        len(df)
    )

    print("\nBooks by category:")

    print(
        df["category"].value_counts()
    )

    print("\nFirst 5 rows:")

    print(
        df.head()
    )

    df.to_csv(
        "data_pipeline/raw_books.csv",
        index=False
    )

    print(
        "\nRaw data saved to "
        "data_pipeline/raw_books.csv"
    )


if __name__ == "__main__":
    main()