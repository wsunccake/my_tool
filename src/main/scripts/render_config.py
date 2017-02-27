#!/usr/bin/env python3

import os
import docopt

from my_tool.file_tool import PyConfig


def main(options):
    config_file = options['--config']
    template_file = options['--template']
    inject_parameter = options['--inject']

    for f in [config_file, template_file]:
        if not os.path.exists(f):
            raise RuntimeError('No found file: {}'.format(f))

    if inject_parameter is None:
        inject_parameter = 'default'

    c = PyConfig(config_file)
    print(c.get_config_dict(inject_parameter))


if __name__ == "__main__":
    option_doc = '''
Usage:
  render_config -c <config_file> [-t <template_file>] [-i <parameter>]

Options:
  -h, --help                       help
  -c, --config <config_file>       config file, config.py
  -t, --template <template_file>   template file, template.j2
  -i, --inject <parameter>         inject parameter,
'''

    options = docopt.docopt(option_doc, version='0.1')
    main(options)
