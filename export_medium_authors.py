import argparse
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

XLS_COLUMNS = [
    'name',
    'medium_url',
    'twitter',
    'linkedin',
    'email',
]


def begin_scraping(url):
    # ORG - https://medium.com/faun/about [org page]
    if 'about' in url:
        authors = get_all_authors_from_org(url)

        data_frame = pd.DataFrame(authors)
        filename = 'Authors for {url} - {datetime}.xls'.format(
            url=url,
            datetime=datetime.now().strftime('%c'),
        )
        data_frame.to_excel(
            filename,
            columns=XLS_COLUMNS,
        )
        print('XLS file created: {filename}')
        return

    print('URL not supported for now.')
    return


def get_all_authors_from_org(url):
    """
    :param url: Medium about page of an org. E.g: medium.com/faun/about
    """
    response = requests.get(url)
    page = BeautifulSoup(response.text)

    # Try to get name, cotact details: twitter, linkedin, email
    writers_data = []

    writers_div = page.find_all('div', class_='infoCard')

    for writer in tqdm(writers_div):
        data = {
            'twitter': '',
            'linkedin': '',
            'email': '',
        }

        author_details = writer.find('a', class_='link--primary')
        author_name = author_details.text
        author_medium_url = author_details.attrs['href']

        if not author_name:
            continue

        data['name'] = author_name
        data['medium_url'] = author_medium_url

        contact_details = get_contact_details_from_medium_user(author_medium_url)
        time.sleep(5)

        data['twitter'] = contact_details.get('twitter')
        data['linkedin'] = contact_details.get('linkedin')

        writers_data.append(data)

    return writers_data


def get_contact_details_from_medium_user(url):
    """
    :param url: medium user URL (e.g: https://medium.com/@imoisharma)

    Try getting the following from Medium user profile:
        Twitter URL
        LinkedIn URL
        Email
    """
    response = requests.get(url)
    page = BeautifulSoup(response.text)
    all_links = page.find_all('a', href=True)
    twitter_links = [
        link.attrs['href'] for link in all_links
        if 'twitter' in link.attrs['href']
    ]
    linkedin_links = [
        link.attrs['href'] for link in all_links
        if 'linkedin.com' in link.attrs['href']
    ]
    emails = [
        link.attrs['href'] for link in all_links
        if 'mailto:' in link.attrs['href']
    ]
    return {
        'twitter': ', '.join(twitter_links),
        'linkedin': ', '.join(linkedin_links),
        'email': ', '.join(emails),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='Medium URL to be scraped for autho')
    arguments = parser.parse_args()

    begin_scraping(arguments.url)
