import os
import tempfile
import unittest

from texpro import *

TEST_FILE_TREE = '''{dir}
├── eq
│   └── test_eq.tex
├── fig
├── img
└── tab'''


class PathTestSuite(unittest.TestCase):
    def test_set_doc_path(self):
        # default path
        # self.assertEqual(config.doc_path, None)

        # setting nonsense relative path
        nonsense_doc_path = 'directorydoesnotexist'
        with self.assertWarns(ResourceWarning):
            config.doc_path = nonsense_doc_path
        self.assertEqual(str(config.doc_path), nonsense_doc_path)

        # save a file -> IOError
        self.assertRaises(IOError, TexEquation, 'test_eq', 'a_b')

        # setting nonsense absolute path
        with self.assertWarns(ResourceWarning):
            config.doc_path = os.path.expanduser('directorydoesnotexist')

        # setting real path
        with tempfile.TemporaryDirectory() as tmp_doc_path:
            config.doc_path = tmp_doc_path

            # default directories
            self.assertEqual(str(config.abspath(config.img_path)), os.path.join(tmp_doc_path, 'img'))

    def test_make_folders(self):
        # setting real path
        with tempfile.TemporaryDirectory() as tmp_doc_path:
            config.doc_path = tmp_doc_path

            # make_folders with default directories
            config.make_folders()

            # test if directories exist
            self.assertTrue(os.path.isdir(os.path.join(tmp_doc_path, 'eq')))
            self.assertTrue(os.path.isdir(os.path.join(tmp_doc_path, 'img')))
            self.assertTrue(os.path.isdir(os.path.join(tmp_doc_path, 'fig')))
            self.assertTrue(os.path.isdir(os.path.join(tmp_doc_path, 'tab')))

    def test_save_file(self):
        # setting real path
        with tempfile.TemporaryDirectory() as tmp_doc_path:
            config.doc_path = tmp_doc_path

            # make_folders with default directories
            config.make_folders()

            # save equation
            TexEquation('test_eq', 'a_b').save()

            # test file exists
            self.assertTrue(os.path.exists(os.path.join(tmp_doc_path, 'eq', 'test_eq.tex')))

    def test_file_tree(self):
        # setting real path
        with tempfile.TemporaryDirectory() as tmp_doc_path:
            config.doc_path = tmp_doc_path

            # make_folders with default directories
            config.make_folders()

            # save equation
            TexEquation('test_eq', 'a_b').save()

            # test file tree
            self.assertEqual(config.file_tree, TEST_FILE_TREE.format(dir=tmp_doc_path))

    def test_set_paths(self):
        ...
        # custom path if doc_path not set

        # custom directories, including creating object
