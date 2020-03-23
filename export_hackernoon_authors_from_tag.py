import argparse
import logging
import time
from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm


def get_author_urls_from_tag(driver, tag):
    tag_url = f'https://hackernoon.com/tagged/{tag}'
    author_urls = set()

    # get authors from tag page
    driver.get(tag_url)
    time.sleep(5)

    while True:
        stories = driver.find_element_by_class_name('stories-list')
        authors = stories.find_elements_by_class_name('profile')

        for author in authors:
            full_author_url = f'https://hackernoon.com/{author.text}'
            author_urls.add(full_author_url)

        try:
            go_to_next_page_element = driver.find_element_by_xpath('//a[contains(@aria-label,"Next")]')
        except NoSuchElementException:
            print('Reached end of page.')
            break

        go_to_next_page_element.click()
        time.sleep(2)

    return author_urls


def get_author_contact_details(author_url, driver):
    """
    :param author_url: hackernoon profile (e.g: https://hackernoon.com/@scraperboy)
    :param driver: `selenium.webdriver.ChromeDriver`
    """
    data = {
        'hackernoon': author_url,
        'name': None,
        'position': None,
        'twitter': None,
        'facebook': None,
        'linkedin': None,
        'github': None,
    }
    driver.get(author_url)
    time.sleep(2)
    profile_details = driver.find_element_by_class_name('name')
    name_and_position = profile_details.text.split('\n')

    data['name'] = name_and_position[0]

    if len(name_and_position) > 1:
        data['position'] = name_and_position[1]

    contact_details = profile_details.find_elements_by_tag_name('a')

    for a_tag in contact_details:
        url = a_tag.get_property('href')

        if 'twitter.com' in url:
            data['twitter'] = url
        elif 'facebook.com' in url:
            data['facebook'] = url
        elif 'linkedin.com' in url:
            data['linkedin'] = url
        elif 'github.com' in url:
            data['github'] = url

    return data


def export_authors_as_xls(authors, tag):
    xls_columns = [
        'hackernoon',
        'name',
        'position',
        'twitter',
        'facebook',
        'linkedin',
        'github',
    ]
    now = datetime.now().strftime('%c')
    data_frame = pd.DataFrame(authors)
    filename = f'Authors for Hackernoon tag: {tag} - {now}'
    data_frame.to_excel(
        filename,
        columns=xls_columns,
    )
    print('XLS file created: %s' % filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tag', help='Hackernoon article tag. E.g: kubernetes, devops, backend')
    arguments = parser.parse_args()

    driver = webdriver.Chrome()
    author_urls = get_author_urls_from_tag(driver, arguments.tag)
    authors_data = []

    for url in tqdm(author_urls):
        try:
            authors_data.append(
                get_author_contact_details(url, driver)
            )
        except Exception as e:
            if '404' in driver.page_source:
                print('Hackernoon profile %s not found' % url)
                continue
            import pdb; pdb.set_trace()

        export_authors_as_xls(authors_data, arguments.tag)
    except Exception as e:
        print('xls export failed')
        import pdb; pdb.set_trace()
