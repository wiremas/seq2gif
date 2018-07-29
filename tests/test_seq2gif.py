import os
import sys
import shutil
import unittest
import subprocess
from contextlib import contextmanager

from bin import seq2gif
reload(seq2gif)

class TestSeq2Gif(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'tmp')
        self.test_dir = os.path.dirname(self.tmp_dir)
        self.tmp_output = os.path.join(self.tmp_dir, 'test_out.gif')

        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        dummy_input = os.path.join(self.test_dir, 'test_data', '*.jpg')
        args = {'input': [dummy_input],
                'output': self.tmp_output,
                'framesPerSecond': 5,
                'resize': [125, 125, 250, 250],
                'show': None}

        self.dummy = seq2gif.Seq2Gif(args)

    def tearDown(self):

        shutil.rmtree(self.tmp_dir)

    def test_inuput_validation(self):

        test_seq = []
        self.assertFalse(self.dummy.validate_input(test_seq))

        test_seq = ['/some/invalid/path']
        self.assertFalse(self.dummy.validate_input(test_seq))

        test_seq = [os.path.join(self.test_dir, 'test_data', 'number_1.jpg')]
        self.assertFalse(self.dummy.validate_input(test_seq))

        test_seq = [os.path.join(self.test_dir, 'test_data', 'number_1.jpg'),
                    os.path.join(self.test_dir, 'test_data', 'number_2.jpg'),
                    os.path.join(self.test_dir, 'test_data', 'number_3.jpg')]
        self.assertTrue(len(self.dummy.validate_input(test_seq)) == 3)

        test_seq = [os.path.join(self.test_dir, 'test_data', '*.jpg')]
        self.assertTrue(len(self.dummy.validate_input(test_seq)) == 4)

    def test_output_validation(self):

        test_output = ' ' # this is the same as cwd
        self.assertFalse(self.dummy.validate_output(test_output))

        test_output = '/some/invalid/path'
        self.assertFalse(self.dummy.validate_output(test_output))

        with mock_input('yes'):
            test_output = os.path.join(self.test_dir, 'test_data', 'sample.gif')
            self.assertEqual(self.dummy.validate_output(test_output), test_output)

        with mock_input('no'):
            test_output = os.path.join(self.test_dir, 'test_data', 'sample.gif')
            self.assertFalse(self.dummy.validate_output(test_output))

    def test_size_validation(self):

        test_size = []
        self.assertFalse(self.dummy.validate_size(test_size))

        test_size = ['a', 'b', 'c', 'd']
        self.assertFalse(self.dummy.validate_size(test_size))

        test_size = [1, 2, 3, 4.0]
        self.assertEqual(self.dummy.validate_size(test_size), map(float, test_size))


    def test_run_resize(self):

        self.dummy.run_command()

        dummy_seq = self.dummy.images
        dummy_tmp_files = self.dummy.tmp_files

        self.assertTrue(os.path.isfile(self.dummy.output_name))
        self.assertNotEqual(dummy_seq, dummy_tmp_files)
        self.assertFalse(any(self.assertFalse(os.path.isfile(f)) for f in dummy_tmp_files))

    def test_run(self):

        self.dummy.size = None
        self.dummy.run_command()

        dummy_seq = self.dummy.images
        dummy_tmp_files = self.dummy.tmp_files

        self.assertFalse(dummy_tmp_files)
        self.assertTrue(os.path.isfile(self.dummy.output_name))


@contextmanager
def mock_input(mock):
    orig_raw = __builtins__.raw_input
    __builtins__.raw_input = lambda _: mock
    yield
    __builtins__.raw_input = orig_raw


if __name__ == '__main__':
    unittest.main()
