import os
import unittest

from my_tool.file_tool import PyConfig


class PyConfigTest(unittest.TestCase):
    def setUp(self):
        self.config_file = 'tmp.py'
        config_py = '''
username = 'user'
password = 'password'
email = '{}@email.com'.format(username)

project_path = {'default': '/app', 'lib': '/lib'}
'''
        self.project_path = {'default': '/app', 'lib': '/lib', 'app': '/app'}
        with open(self.config_file, 'w') as f:
            f.write(config_py)

    def tearDown(self):
        os.remove(self.config_file)

    def test_get_config_dict(self):
        config_object = PyConfig(self.config_file)

        for k, v in self.project_path.items():
            self.assertEqual(config_object.get_config_dict(k)['project_path'], v)
