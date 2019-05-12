#!/use/bin/env python3

import re
import os
import logging
import functools
import time
from concurrent import futures

import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logfile = 'download.log'
fh = logging.FileHandler(logfile, mode='a')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

MAX_WORKERS = 5


def log(function):
    @functools.wraps(function)
    def wrapper(*args):
        logger.debug('Function: {}'.format(function.__name__))
        logger.debug('Args: {}'.format(*args))
        return function(*args)

    return wrapper


@log
def get_detail_page(browse_mame_page, prefix_url='https://edgeemu.net/'):
    href_pattern = '<a href="details.*.htm">'
    html_pattern = r'"(.*htm)"'

    response = requests.get(browse_mame_page)
    logger.debug('HTTP Return: {}'.format(response.status_code))
    if response.status_code != requests.codes.ok:
        return []

    match_all = re.findall(href_pattern, response.text)
    logger.debug('Match URL: ' + ' '.join(match_all))
    return [prefix_url + re.search(html_pattern, s).groups()[0] for s in match_all if re.search(html_pattern, s)]


@log
def get_download_page(detail_page, prefix_url='https://edgeemu.net/'):
    id_pattern = r'<a href="(.*.id=\d+)"'

    response = requests.get(detail_page)
    logger.debug('HTTP Return: {}'.format(response.status_code))
    if response.status_code != requests.codes.ok:
        return None

    matcher = re.search(id_pattern, response.text)
    if matcher:
        logger.info('Download page: {}'.format(prefix_url + matcher.groups()[0]))
        return prefix_url + matcher.groups()[0]

    return None


@log
def download_file(download_url, folder='.'):
    id_pattern = r'id=(\d+)'
    file_pattern = r'filename="(.*.zip)"'

    filename = re.search(id_pattern, download_url).groups()[0] + '.zip'
    with requests.get(download_url, stream=True) as response:
        logger.debug('HTTP Return: {}'.format(response.status_code))
        response.raise_for_status()

        if response.headers.get('Content-Disposition'):
            matcher = re.search(file_pattern, response.headers.get('Content-Disposition'))
            if matcher:
                filename = matcher.groups()[0]
        filename = os.path.join(folder, filename)
        logger.info('{} save to {}'.format(download_url, filename))

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    f.flush()
    return filename


if __name__ == '__main__':
    rom_url = 'https://edgeemu.net/browse-mame-Y.htm'
    destination_dir = 'roms'

    if not os.path.exists(destination_dir):
        os.mkdir(destination_dir, 0o755)

    start_time = time.time()
    pages = get_detail_page(rom_url)

    # simple
    # for p in pages:
    #     download_file(get_download_page(p), destination_dir)

    # multi thread
    workers = min(MAX_WORKERS, len(pages))
    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(lambda u: download_file(get_download_page(u), destination_dir), pages)

    end_time = time.time()
    print('run time:', end_time - start_time)

