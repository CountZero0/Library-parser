import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def main():
    Path("books").mkdir(exist_ok=True)
    Path("images").mkdir(exist_ok=True)

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
        image_url_path = soup.find('div', class_='bookimage').find('img').get('src')
        image_url = urljoin(book_url, image_url_path)
        download_books(book_id, response, title)
        download_book_covers(image_url)


def download_book_covers(url, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    image_name = str(urlsplit(url).path.split('/')[-1])
    file_path = os.path.join(folder, image_name)

    with open(file_path, "wb") as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_books(book_id, response, title, folder='books/'):
    filename = f'{book_id}. {title}.txt'
    safe_filename = sanitize_filename(filename)
    file_path = os.path.join(folder, safe_filename)

    with open(file_path, "w", encoding='utf-8') as file:
        file.write(response.text)

    return safe_filename


if __name__ == "__main__":
    main()
