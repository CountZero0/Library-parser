import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import tqdm as t


def main():
    Path("books").mkdir(exist_ok=True)
    Path("images").mkdir(exist_ok=True)
    Path("comments").mkdir(exist_ok=True)

    for book_id in t(range(1, 10), desc='Parsing online library', colour='MAGENTA', ncols=100):
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
        parsed_info = parse_book_page(soup, book_url)

        download_books(book_id, response, parsed_info['title'])
        download_book_covers(parsed_info['image_url'])
        download_book_comments(book_id, parsed_info['author'], parsed_info['comments'])


def parse_book_page(soup, book_url):
    title, author = soup.find('table').find('h1').text.split('::')

    image_url_path = soup.find('div', class_='bookimage').find('img').get('src')

    genre_tag = soup.find('span', class_='d_book').find_all('a')

    comments_tag = soup.find_all('div', class_='texts')
    comments = ''
    for comment in comments_tag:
        comments += comment.find('span', class_='black').text + '\n'

    book_parsed_page = {
        'title': title.strip(),
        'author': author.strip(),
        'genre': [genre.text for genre in genre_tag],
        'image_url': urljoin(book_url, image_url_path),
        'comments': comments
    }
    return book_parsed_page


def download_book_comments(book_id, author, comments, folder='comments/'):
    file_name = f"{book_id}. {author}"
    filepath = os.path.join(folder, file_name)

    if comments:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(comments)


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
