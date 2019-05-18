#!/use/bin/env python3

import re
import os
import logging
import functools
import time
from concurrent import futures
import asyncio

import requests
import aiohttp

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

    logger.info('Detail page: {}'.format(detail_page))
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


@log
async def async_get_download_page(detail_page, prefix_url='https://edgeemu.net/'):
    id_pattern = r'<a href="(.*.id=\d+)"'

    logger.info('Detail page: {}'.format(detail_page))

    async with aiohttp.ClientSession() as session:
        async with session.get(detail_page) as response:
            logger.debug('HTTP Return: {}'.format(response.status))
            if response.status != 200:
                return None
            matcher = re.search(id_pattern, await response.text())
            if matcher:
                logger.info('Download page: {}'.format(prefix_url + matcher.groups()[0]))
                return prefix_url + matcher.groups()[0]
    return None


@log
async def async_download_file(download_url, folder='.'):
    id_pattern = r'id=(\d+)'
    file_pattern = r'filename="(.*.zip)"'

    filename = re.search(id_pattern, download_url).groups()[0] + '.zip'

    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as response:
            logger.debug('HTTP Return: {}'.format(response.status))
            if response.status != 200:
                return None

            if response.headers.get('Content-Disposition'):
                matcher = re.search(file_pattern, response.headers.get('Content-Disposition'))
                if matcher:
                    filename = matcher.groups()[0]

            filename = os.path.join(folder, filename)
            logger.info('{} save to {}'.format(download_url, filename))

            chunk_size = 8192
            with open(filename, 'wb') as fd:
                while True:
                    chunk = await response.content.read(chunk_size)
                    if not chunk:
                        break
                    fd.write(chunk)
                    fd.flush()

    return filename


async def async_action(download_url, folder='.'):
    await async_download_file(await async_get_download_page(download_url), folder)


def test_performance(rom_url):
    pages = get_detail_page(rom_url)

    start_time = time.time()
    [get_download_page(u) for u in pages]
    end_time = time.time()
    logger.info('single thread run time: {}'.format(end_time - start_time))

    start_time = time.time()
    workers = min(MAX_WORKERS, len(pages))
    with futures.ThreadPoolExecutor(workers) as executor:
        executor.map(get_download_page, pages)
    end_time = time.time()
    logger.info('multi thread run time: {}'.format(end_time - start_time))

    start_time = time.time()
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(async_get_download_page(u)) for u in pages]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    end_time = time.time()
    logger.info('async run time: {}'.format(end_time - start_time))


def main(rom_url, destination_dir='roms', work_type='async'):
    if not os.path.exists(destination_dir):
        os.mkdir(destination_dir, 0o755)

    pages = get_detail_page(rom_url)
    start_time = time.time()

    if work_type is 'async':
        # async
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(async_action(u, destination_dir)) for u in pages]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
    elif work_type is 'multi':
        # multi thread
        workers = min(MAX_WORKERS, len(pages))
        with futures.ThreadPoolExecutor(workers) as executor:
            res = executor.map(lambda u: download_file(get_download_page(u), destination_dir), pages)
    else:
        # single thread
        for p in pages:
            download_file(get_download_page(p), destination_dir)

    end_time = time.time()
    logger.info('run time: {}'.format(end_time - start_time))


if __name__ == '__main__':
    rom_urls = ['https://edgeemu.net/browse-mame-Y.htm']

    for url in rom_urls:
        # test_performance(url)
        main(url)
