import os
import unittest

from my_tool.web_tool import WebComic, WebTool


class WebToolTest(unittest.TestCase):
    def test_save_image(self):
        picture_url = 'https://www.python.org/static/img/python-logo@2x.png'
        filename = 'python-logo.png'

        WebTool.save_image(picture_url, filename)

        self.assertTrue(os.path.isfile(filename))
        self.assertGreater(os.stat(filename).st_size, 15000, 'picture size about 15k')

        os.remove(filename)


class WebComicTest(unittest.TestCase):
    def test_get_image_urls(self):
        pass

    def test_pickup_url(self):
        pass

    def test_download_picture(self):
        url = 'http://comic.ck101.com/vols/2792/1'
        start_page = 1
        end_page = 3
        wc = WebComic(url, end_page, start_page)

        wc.download_picture()

        for i in range(start_page, end_page+1):
            self.assertTrue(os.path.isfile('{}.jpg'.format(i)))

        for i in range(start_page, end_page+1):
            os.remove('{}.jpg'.format(i))
