import pandas as pd


RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


def clean_price(value):
    """
    Convert price text such as £51.77 or Â£51.77 into 51.77.
    """

    try:
        price = str(value).replace("Â", "").replace("£", "").strip()
        return float(price)
    except (ValueError, TypeError):
        return None



def clean_rating(value):
    """
    Convert text rating into an integer from 1 to 5.
    """

    return RATING_MAP.get(value)


def clean_availability(value):
    """
    Convert availability text into True/False.
    """

    if pd.isna(value):
        return None

    return "In stock" in str(value)


def main():

    # Load raw scraped data
    df = pd.read_csv(
        "data_pipeline/raw_books.csv"
    )

    print("Raw data:")
    print(df.head())

    # Clean price
    df["price_gbp"] = df["price"].apply(
        clean_price
    )

    # Clean rating
    df["rating"] = df["star_rating"].apply(
        clean_rating
    )

    # Clean availability
    df["in_stock"] = df["availability"].apply(
        clean_availability
    )

    # Remove original unclean columns
    df = df.drop(
        columns=[
            "price",
            "star_rating",
            "availability"
        ]
    )

    # Handle invalid numeric values using median
    if df["price_gbp"].isnull().any():
        median_price = df["price_gbp"].median()

        df["price_gbp"] = df["price_gbp"].fillna(
            median_price
        )

    if df["rating"].isnull().any():
        median_rating = df["rating"].median()

        df["rating"] = df["rating"].fillna(
            median_rating
        )

    # Convert rating to integer
    df["rating"] = df["rating"].round().astype(int)

    # Convert price to INR
    GBP_TO_INR = 105.50

    df["price_inr"] = (
        df["price_gbp"] * GBP_TO_INR
    ).round(2)

    # Ensure boolean type
    df["in_stock"] = df["in_stock"].fillna(False).astype(bool)

    print("\nCleaned data:")
    print(df.head())

    print("\nData types:")
    print(df.dtypes)

    print("\nTotal books:")
    print(len(df))

    print("\nBooks by category:")
    print(df["category"].value_counts())

    # Save cleaned data
    df.to_csv(
        "data_pipeline/cleaned_books.csv",
        index=False
    )

    print(
        "\nCleaned data saved to "
        "data_pipeline/cleaned_books.csv"
    )


if __name__ == "__main__":
    main()
