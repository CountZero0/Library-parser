import argparse
import json
import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests
from tqdm import tqdm as t

from parse_tululu_category import get_books_ids


def create_parser():
    parser = argparse.ArgumentParser(description='Programm parse online library tululu.prg')
    parser.add_argument('-sp','--start_page_id', help='Page id, with you start parsing', type=int, default=1)
    parser.add_argument('-ep', '--end_page_id', help='Page id, with you end parsing', type=int, default=2)
    parser.add_argument('--filename', default='books.json', help='Title of your future json')
    
    return parser.parse_args()


def main():
    books = []
    args = create_parser()
    ids = get_books_ids(args.start_page_id, args.end_page_id)

    for book_id in t(ids, desc='Parsing online library', colour='MAGENTA', ncols=120):
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
        
        book_parsed_page = {
            'title': parsed_info[0],
            'author': parsed_info[1],
            'image_path': download_book_covers(parsed_info[2]),
            'book_path': download_books(book_id, response, parsed_info[0]),
            'comments': parsed_info[-1],
            'genres': parsed_info[-2]
        }
        books.append(book_parsed_page)
        download_book_comments(book_id, parsed_info[0], parsed_info[-1])
    
    make_json(args.filename, books)


def parse_book_page(soup, book_url):
    title, author = soup.select_one('table h1').text.split('::')
    
    image_tag = soup.select_one('div.bookimage img').get('src')
    image_url = urljoin('http://tululu.org', image_tag)

    genres = [genre.text for genre in soup.select('span.d_book a')]

    book_comments = [comment.select_one('span.black').text for comment in soup.select('div.texts')]
    
    return title.strip(), author.strip(), image_url, genres, book_comments


def download_book_comments(book_id, title, comments, folder='comments/'):
    file_name = f"{book_id}. {title}"
    file_path = os.path.join(folder, file_name)

    if comments:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(''.join(comments))

    return file_path


def download_book_covers(url, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()

    image_name = str(urlsplit(url).path.split('/')[-1])
    file_path = os.path.join(folder, image_name)
    
    with open(file_path, "wb") as file:
        file.write(response.content)

    return file_path


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_books(book_id, response, title, folder='books/'):
    filename = f'{book_id}. {title}.txt'
    safe_filename = sanitize_filename(filename)
    file_path = os.path.join(folder, safe_filename)

    with open(file_path, "w", encoding='utf-8') as file:
        file.write(response.text)

    return file_path


def make_json(filename, books):
    with open(filename, 'w') as file:
        json.dump(books, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    Path("books").mkdir(exist_ok=True)
    Path("images").mkdir(exist_ok=True)
    Path("comments").mkdir(exist_ok=True)
    
    main()
