from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


def get_books_ids(start_page_id, end_page_id):
    book_ids = []

    for page_id in range(start_page_id, end_page_id + 1):
        category_url = f"http://tululu.org/l55/{page_id}/"
        response = requests.get(category_url, allow_redirects=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        book_ids += [book_id.select_one('a')['href'][2:-1] for book_id in soup.select('table.d_book')]
    
    return book_ids
