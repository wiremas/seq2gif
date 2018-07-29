#!/usr/bin/env python

import os
import sys
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop

class InstallCommand(install):

    def run(self):
        cmd_script = set_up()
        install.run(self)


class DevelopCommand(develop):

    def run(self):
        cmd_script = set_up()
        develop.run(self)


def set_up():
    """ symlink the seq2gif module to a file without .py extension.
    this file will be copied to /usr/local/bin so that we can call it directly
    without the need to add .py to the command """

    bin_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bin')
    cmd_module = os.path.join(bin_path, 'seq2gif.py')
    cmd_script = os.path.join(bin_path, 'seq2gif')

    if not os.path.isfile(cmd_script):
        os.symlink(cmd_module, cmd_script)
        sys.stdout.write('Created command symlink: {}\n'.format(cmd_script))
        return cmd_script


setup(name='seq2gif',
      version='1.0',
      description='Convert image sequence to gif',
      author='Anno Schachner',
      author_email='anno.schachner@gmail.com',
      packages=['bin', 'tests'],
      scripts=['bin/seq2gif'],
      cmdclass={'install': InstallCommand,
                'develop': DevelopCommand},
      install_requires=['imageio', 'pillow', 'Qt.py']
     )

