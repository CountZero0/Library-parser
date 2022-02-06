# Book parser for tululu.org

This programm download books, and all stuff according to books: covers, titles, authors and comments people left to these books

## How to install

Python3 should be installed. At first, clone repository, then to install all dependencies use this command in terminal:

```pip install -r requirements.txt```

## To run

Use this command:

```python books.py --start_id --end_id```

* `--start_id` or `-si`- page id with which you start downloading
* `--end_id` or `-ei`- page id with which you end downloading
* `--filename` - the name of json file