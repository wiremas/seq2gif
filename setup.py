#!/usr/bin/env python

import os
import sys
from setuptools import setup

def set_up():
    """ make symlink for pretty command """
    bin_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bin')
    cmd_module = os.path.join(bin_path, 'seq2gif.py')
    cmd_script = os.path.join(bin_path, 'seq2gif')
    os.symlink(cmd_module, cmd_script)

def clean_up():
    bin_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bin')
    cmd_script = os.path.join(bin_path, 'seq2gif')
    os.remove(cmd_script)

if __name__ == '__main__':
    if '--uninstall' in sys.argv:
        clean_up()
    else:
        set_up()

setup(name='seq2gif',
      version='1.0',
      description='Convert image sequence to gif',
      author='Anno Schachner',
      author_email='anno.schachner@gmail.com',
      packages=['bin', 'tests'],
      scripts=['bin/seq2gif'],
      install_requires=['imageio', 'pillow', 'Qt.py']
     )

