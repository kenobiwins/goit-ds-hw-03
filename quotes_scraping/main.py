import os
import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient


class MongoDB:
    def __init__(self, uri, db_name):

        self.client = MongoClient(uri)
        self.db = self.client[db_name]

        self.quotes_collection = self.db["quotes"]
        self.authors_collection = self.db["authors"]

        print(f"Connected to MongoDB database: {db_name}")

    def insert_quotes(self, quotes_data):
        print("Inserting quotes into MongoDB...")
        self.quotes_collection.insert_many(quotes_data)
        print(f"{len(quotes_data)} quotes inserted.")

    def insert_authors(self, authors_data):
        print("Inserting authors into MongoDB...")
        self.authors_collection.insert_many(authors_data)
        print(f"{len(authors_data)} authors inserted.")

    def close(self):
        self.client.close()
        print("MongoDB connection closed.")


class QuotesScraper:
    def __init__(self):
        self.base_url = "http://quotes.toscrape.com/page/"
        self.quotes = []
        self.authors = []
        self.output_folder = "output"

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def scrape(self):
        page = 1
        while True:
            url = self.base_url + str(page)
            print(f"Scraping page {page}...")  
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            quotes_list = soup.find_all("div", class_="quote")
            if not quotes_list:
                print(f"No more quotes found on page {page}.")
                break

            for quote_div in quotes_list:
                quote_text = quote_div.find("span", class_="text").get_text()
                author_name = quote_div.find("small", class_="author").get_text()
                tags = [tag.get_text() for tag in quote_div.find_all("a", class_="tag")]

                print(f"Scraped quote by {author_name}: {quote_text}")

                self.quotes.append(
                    {"tags": tags, "author": author_name, "quote": quote_text}
                )

                if not self.author_exists(author_name):
                    print(f"Scraping author details for {author_name}...")
                    author_url = quote_div.find("a")["href"]
                    author_page = requests.get(
                        "http://quotes.toscrape.com" + author_url
                    )
                    author_soup = BeautifulSoup(author_page.text, "html.parser")

                    born_date = author_soup.find(
                        "span", class_="author-born-date"
                    ).get_text()
                    born_location = author_soup.find(
                        "span", class_="author-born-location"
                    ).get_text()
                    description = (
                        author_soup.find("div", class_="author-description")
                        .get_text()
                        .strip()
                    )

                    self.authors.append(
                        {
                            "fullname": author_name,
                            "born_date": born_date,
                            "born_location": born_location,
                            "description": description,
                        }
                    )
                    print(f"Scraped author details for {author_name}")

            page += 1

        print("Scraping completed. Saving data to JSON files...")
        self.save_to_json()

    def author_exists(self, author_name):
        for author in self.authors:
            if author["fullname"] == author_name:
                return True
        return False

    def save_to_json(self):
        quotes_file_path = os.path.join(self.output_folder, "quotes.json")
        authors_file_path = os.path.join(self.output_folder, "authors.json")

        with open(quotes_file_path, "w", encoding="utf-8") as quotes_file:
            json.dump(self.quotes, quotes_file, ensure_ascii=False, indent=4)

        with open(authors_file_path, "w", encoding="utf-8") as authors_file:
            json.dump(self.authors, authors_file, ensure_ascii=False, indent=4)

        print(f"Data has been saved to {quotes_file_path} and {authors_file_path}.")


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    scraper = QuotesScraper()
    scraper.scrape()

    uri = "mongodb://localhost:27017/"
    db_name = "quotes_scraper_db" 

    quotes_data = load_json("output/quotes.json")
    authors_data = load_json("output/authors.json")

    mongo_db = MongoDB(uri, db_name)
    mongo_db.insert_quotes(quotes_data)
    mongo_db.insert_authors(authors_data)

    mongo_db.close()
