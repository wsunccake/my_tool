import docopt
import logging
from my_tool.web_tool import WebComic


def main(options):
    web_url = options['--web_url']
    final_page = int(options['--final_page'])
    start_page = int(options['--start_page'])

    if start_page is None:
        start_page = 1
    else:
        start_page = int(start_page)


    wc = WebComic(web_url, final_page, start_page)
    wc.download_picture()


if __name__ == "__main__":
    option_doc = '''
Usage:
  cat_pic -u <web_url> -f <final_page> [-s <start_page>]

Options:
  -h, --help                       help
  -u, --web_url <web_url>          web url, http://xxx.comic/vols/123
  -f, --final_page <final_page>    final page, ie 10
  -s, --start_page <start_page>    start page, ie 1
'''

    options = docopt.docopt(option_doc, version='0.1')
    main(options)
