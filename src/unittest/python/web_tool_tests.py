import os
import unittest

from my_tool.web_tool import WebComic, WebTool


class WebToolTest(unittest.TestCase):
    def setUp(self):
        self.picture_url = 'https://www.python.org/static/img/python-logo@2x.png'
        self.filename = 'python-logo.png'

    def tearDown(self):
        os.remove(self.filename)

    def test_save_image(self):
        WebTool.save_image(self.picture_url, self.filename)

        self.assertTrue(os.path.isfile(self.filename))
        self.assertGreater(os.stat(self.filename).st_size, 15000, 'picture size about 15k')


class WebComicTest(unittest.TestCase):
    def setUp(self):
        self.url = 'http://comic.ck101.com/vols/2792/1'
        self.start_page = 1
        self.end_page = 3

    def tearDown(self):
        for i in range(self.start_page, self.end_page+1):
            os.remove('{}.jpg'.format(i))

    def test_get_image_urls(self):
        pass

    def test_pickup_url(self):
        pass

    def test_download_picture(self):
        wc = WebComic(self.url, self.end_page, self.start_page)
        wc.download_picture()

        for i in range(self.start_page, self.end_page+1):
            self.assertTrue(os.path.isfile('{}.jpg'.format(i)))
