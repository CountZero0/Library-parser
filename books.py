from cgitb import reset
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def download_txt():
    Path("books").mkdir(exist_ok=True)

    for book_id in range(1, 11):
        book_url = f"https://tululu.org/txt.php?id={book_id}"
        parse_url = f"https://tululu.org/b{book_id}/"
        response = requests.get(book_url)
        parse_response = requests.get(parse_url)

        try:
            response.raise_for_status()
            parse_response.raise_for_status()
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            continue

        soup = BeautifulSoup(parse_response.text, 'lxml')
        book_title = soup.find('table').find('h1')
        title = book_title.text.strip().split('::')[0].strip()
        extract_book(book_id, response, title)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def extract_book(book_id, response, title, folder="books/"):
    filename = f'{book_id}. {title}.txt'
    safe_filename = sanitize_filename(filename)
    file_path = os.path.join(folder, safe_filename)

    with open(file_path, "w", encoding='utf-8') as file:
        file.write(response.text)

    return safe_filename


if __name__ == "__main__":
    download_txt()
