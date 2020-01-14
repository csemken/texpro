import os
import tempfile
import unittest

from texpro import *


class PathTestSuite(unittest.TestCase):
    def test_doc_path(self):
        # default path
        self.assertEqual(config.doc_path, None)

        # setting nonsense relative path
        nonsense_doc_path = 'directorydoesnotexist'
        with self.assertWarns(ResourceWarning):
            config.doc_path = nonsense_doc_path
        self.assertEqual(config.doc_path, nonsense_doc_path)

        # TODO save a file -> IOError

        # setting nonsense absolute path
        with self.assertWarns(ResourceWarning):
            config.doc_path = os.path.expanduser('directorydoesnotexist')

        # setting real path
        with tempfile.TemporaryDirectory() as tmp_doc_path:
            config.doc_path = tmp_doc_path

            # default directories
            self.assertEqual(config.abspath(config.img_path), os.path.join(tmp_doc_path, 'img'))
            self.assertEqual(config.fig2img_path, os.path.join('..', 'img'))

            # TODO create folder, save file

            # TODO custom directories, including creating object