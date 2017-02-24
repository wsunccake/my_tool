import requests
import os
import re
import logging

logging.basicConfig(level=logging.INFO, filename='{}.log'.format(__name__),
                    format='%(asctime)s | %(levelname)s | %(funcName)s |%(message)s')


class WebTool(object):
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    @staticmethod
    def init_config(header=None):
        if header:
            WebTool.header = header

    @staticmethod
    def save_image(url, filename=None, overwrite=False):
        if filename is None:
            filename = '{}'.format(url.split('/')[-1])
            logging.debug('update filename to {}'.format(filename))

        logging.info('image url: {}'.format(url))
        logging.info('filename: {}'.format(filename))

        if os.path.exists(filename) and overwrite is False:
            return

        html = requests.get(url, headers=WebTool.header)

        r = requests.get(url, stream=True, cookies=html.cookies, headers=WebTool.header)
        with open(filename, 'wb') as f:
            logging.info('download {} -> {}'.format(url, filename))
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)


class WebComic(object):
    def __init__(self, url, end_page=10, start_page=1, suffix='jpg'):
        self.header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.__exclude_files = ['pageImg.jpg']
        self.__web_url = url
        self.__start_page = start_page
        self.__final_page = end_page
        self.__filename_suffix = suffix

    @property
    def web_url(self):
        return self.__web_url

    @web_url.setter
    def web_url(self, url):
        self.__web_url = url

    @property
    def start_page(self):
        return self.__start_page

    @start_page.setter
    def start_page(self, page):
        self.__start_page = page

    @property
    def final_page(self):
        return self.__final_page

    @final_page.setter
    def final_page(self, page):
        self.__final_page = page

    @property
    def filename_suffix(self):
        return self.__filename_suffix

    @filename_suffix.setter
    def filename_suffix(self, suffix):
        self.__filename_suffix = suffix

    def get_image_urls(self, url, suffix):
        html = requests.get(url, headers=self.header)

        logging.info('URL: {}, suffix: {}'.format(url, suffix))
        logging.debug(html.text)

        pattern = 'http://.*?\.{}'.format(suffix)
        image_urls = re.findall(pattern, html.text)

        logging.info('URLs: {}'.format(image_urls))
        return image_urls

    def pickup_url(self, urls):
        url = ''
        max_size = 0

        for u in set(urls):
            if u.split('/')[-1] in self.__exclude_files:
                break

            try:
                r_head = requests.head(u, headers=self.header)
                size = r_head.headers['content-length']
                logging.debug('{}, size: {}'.format(u, size))

                if int(size) > int(max_size):
                    url = u
                    max_size = size

            except Exception as e:
                logging.error(e)

        logging.info('URL: {}'.format(url))
        return url

    def download_picture(self):
        http_pattern = re.compile('http(s)?:\/\/.*')

        for i in range(self.start_page, self.final_page + 1):
            urls = self.get_image_urls('{}/{}'.format(self.web_url, i), self.filename_suffix)
            url = self.pickup_url(urls)

            if http_pattern.match(url):
                WebTool.save_image(url, '{}.{}'.format(i, self.filename_suffix))

