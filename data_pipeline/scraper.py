import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd


BASE_URL = "https://books.toscrape.com/"


def get_book_category(book_url):

    response = requests.get(book_url)

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    breadcrumb_links = soup.select(
        "ul.breadcrumb li a"
    )

    if len(breadcrumb_links) >= 3:
        return breadcrumb_links[-1].get_text(
            strip=True
        )

    return None


def scrape_book_details(book, page_url):

    title = book.select_one(
        "h3 a"
    ).get("title")

    price = book.select_one(
        "p.price_color"
    ).get_text(strip=True)

    rating_classes = book.select_one(
        "p.star-rating"
    ).get("class")

    star_rating = rating_classes[1]

    availability = book.select_one(
        "p.instock.availability"
    ).get_text(
        " ",
        strip=True
    )

    book_link = book.select_one(
        "h3 a"
    ).get("href")

    book_url = urljoin(
        page_url,
        book_link
    )

    category = get_book_category(
        book_url
    )

    return {
        "title": title,
        "price": price,
        "star_rating": star_rating,
        "availability": availability,
        "category": category
    }


def scrape_listing_page(page_url):

    response = requests.get(page_url)

    print(
        "Scraping:",
        page_url,
        "| Status:",
        response.status_code
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    books = soup.select(
        "article.product_pod"
    )

    page_books = []

    for book in books:

        book_data = scrape_book_details(
            book,
            page_url
        )

        page_books.append(book_data)

    return page_books


# --------------------------------
# Scrape 5 pages
# --------------------------------

all_books = []

for page_number in range(1, 6):

    if page_number == 1:

        page_url = BASE_URL

    else:

        page_url = (
            f"{BASE_URL}"
            f"catalogue/page-{page_number}.html"
        )

    page_books = scrape_listing_page(
        page_url
    )

    all_books.extend(page_books)

    print(
        f"Books collected so far: "
        f"{len(all_books)}"
    )


# --------------------------------
# Final result
# --------------------------------

print("\n==============================")
print("SCRAPING COMPLETED")
print("==============================")

print(
    "Total books scraped:",
    len(all_books)
)

print(
    "Total categories:",
    len(
        set(
            book["category"]
            for book in all_books
            if book["category"]
        )
    )
)

# --------------------------------
# Convert to DataFrame
# --------------------------------

df = pd.DataFrame(all_books)


print("\nDataFrame shape:")
print(df.shape)


print("\nColumns:")
print(df.columns.tolist())


print("\nFirst 5 books:")
print(df.head())


# --------------------------------
# Category information
# --------------------------------

print("\nNumber of categories:")
print(df["category"].nunique())


print("\nCategory counts:")
print(df["category"].value_counts())


# --------------------------------
# Save raw data
# --------------------------------

df.to_csv(
    "data_pipeline/outputs/scraped_books.csv",
    index=False
)


print(
    "\nRaw data saved successfully to:"
)

print(
    "data_pipeline/outputs/scraped_books.csv"
)