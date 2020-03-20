import requests
from bs4rmport BeautifulSoup
import argparse


def begin_scraping(url):
    # 2 types of pages
    # ORG - medium.com/faun/about [org page]
    if 'about' in url:
        authors = get_all_authors_from_org(url)


    # TAGS - https://hackernoon.com/tagged/kubernetes


    impor


def get_all_authors_from_org(url):
    """
    :param url: Medium about page of an org. E.g: medium.com/faun/about
    """
    response = requests.get(url)
    page = BeautifulSoup(response.text)
    writers_data = []

    writers_div = page.find_all('div', class_='infoCard')

    for writer in writers_div:
        data = {}

        author_name = writer.find('a', class_='link--primary').text

        if not author_name:
            continue

        data['name'] = author_name




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='Medium URL to be scraped for autho')
    begin_scraping()


