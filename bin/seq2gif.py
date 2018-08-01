#!/usr/bin/python

import os
import sys
import glob
import imageio
import tempfile
import argparse
import PIL.Image as pil

class Image(object):
    def __init__(self, path):
        self.path = self._validate_path(path)
        self.image = pil.open(path)

    def _validate_path(self, path):
        path = os.path.realpath(os.path.expanduser(path))
        if os.path.isfile(path):
            return path
        else:
            raise RuntimeError('File does not exist: {}'.format(path))

    def resize(self, size):
        """ resize the image. this method accepts three types of arguments.
        1. size (str) : a number followed by a % sign. scales the image
                        by the given percentage.
        2. size (int) : define the width of the new image. the height will
                        be scaled proportional.
        3. size (int, int) : define width and height of the new image. """

        err_msg = 'Invalid use of argument "resize": \n {}'.format(self.resize.__doc__)
        width = height = 0.0
        if len(size) == 1:
            if isinstance(size[0], str):
                if size[0].endswith('%'):
                    try:
                        width = (self.image.size[0] * int(size[0][:-1])) / 100
                        height = (self.image.size[1] * int(size[0][:-1])) / 100
                    except ValueError:
                        raise RuntimeError(err_msg)
                else:
                    try:
                        width = int(size[0])
                        height = int(self.image.size[1] / (self.image.size[0] / float(width)))
                    except ValueError:
                        raise RuntimeError(err_msg)
        elif len(size) == 2:
            try:
                width, height = [int(length) for length in size]
            except ValueError:
                raise RuntimeError(err_msg)
        else:
            raise RuntimeError(err_msg)
        self.image = self.image.resize((width, height), pil.ANTIALIAS)

    def crop(self, crop_size):
        """ crop the image. the crop_size argument should have eitgher of two formats.
        1. crop_size (int, int) : define width and height of the cropped image
                                starting from the top left corner of the image.
        2. crop_size (int, int, int, int) : define the starting position, from
                                the top left corner as well ass width and
                                height. note: position x must be < width and
                                              position y must be < height! """


        def int_float(val):
            return float(int(val))

        err_msg = 'Invalid use of argument "crop": \n {}'.format(self.crop.__doc__)
        if crop_size:
            try:
                crop_size = map(int_float, crop_size)
                if len(crop_size) == 2:
                    [crop_size.insert(0, 0.0) for _ in range(2)]
                elif len(crop_size) == 4:
                    if crop_size[0] >= crop_size[2]\
                    or crop_size[1] >= crop_size[3]:
                        raise RuntimeError(err_msg)
                    else:
                        crop_size = (crop_size[0], crop_size[1],
                                    crop_size[0] + crop_size[2],
                                    crop_size[1] + crop_size[3])
                else:
                    raise RuntimeError(err_msg)
            except ValueError:
                raise RuntimeError(err_msg)
        self.image = self.image.crop(crop_size)

    def write(self, path):
        pass

    def write_temp(self, suffix='_tmp'):
        tmp_dir = tempfile.gettempdir()
        tmp_name = list(os.path.splitext(os.path.basename(self.path)))
        tmp_name.insert(1, suffix)
        tmp_name = os.path.join(tmp_dir, ''.join(tmp_name))
        self.image.save(tmp_name)
        self.path = tmp_name
        return self.path


class Seq2Gif(object):
    """ Seq2Gif - convert image sequence to gif.  """

    def __init__(self, args):

        self.images = [Image(path) for path in self.validate_input(args['input'])]
        self.output_name = self.validate_output(args['output'])
        self.fps = float(args['framesPerSecond'])
        self.size = args['resize']
        self.crop_size = args['crop']
        self.show = args['show']
        self.tmp_files = []

    def validate_input(self, images):
        """ validate image input and/or find an image sequence.
        :param image: image sequence or single image with wildcard """

        if len(images) == 1:
            if '*' in images[0] or '?' in images[0] or '[' in images[0] or ']' in images[0]:
                wild_card_path = os.path.realpath(os.path.expanduser(images[0]))
                images = sorted(glob.glob(wild_card_path))
                if not images:
                    raise RuntimeError('Could not find a valid image sequence')
                else:
                    return images
            else:
                raise RuntimeError('Not enough input. Only one image given. Use "*" as wildcard to detect an image sequence')
        else:
            for img in images:
                if not os.path.isfile(img):
                    raise RuntimeError('File does not exist: {}'.format(img))
            return images

    def validate_output(self, output_name):
        """ validate out path. """

        output_name = os.path.realpath(os.path.expanduser(output_name)).strip()
        if os.path.isfile(output_name):
            if not user_confirmation('File already exists: {}\nOverwrite? (y)es/(n)o?\n>> '.format(output_name)):
                sys.stdout.write('Aborted by user\n')
                return
        elif os.path.isdir(output_name):
            raise RuntimeError('Output argument must be a file not directory')
        elif not os.path.isdir(os.path.dirname(output_name)):
            raise RuntimeError('Output directory "{}" does not exist\n'.format(os.path.dirname(output_name)))
        elif os.path.splitext(output_name)[-1] != '.gif':
            path, ext = os.path.splitext(output_name)
            output_name = '{}.gif'.format(path)
        return output_name

    def run_command(self):
        """ run the actual command """

        if self.images and self.output_name:
            try:
                self.write_gif()
            except KeyboardInterrupt:
                sys.stdout.write('Aborted by user\n')
            else:
                if self.show:
                    result = pil.open(self.output_name)
                    result.show()
            finally:
                map(os.remove, self.tmp_files)

    def write_gif(self):
        """ write all stored images to gif """

        frames = []
        for i, img in enumerate(self.images):

            progress(i, len(self.images) + 1, 'reading image: "{}"'.format(os.path.basename(img.path)))
            if self.crop_size or self.size:
                if self.crop_size:
                    img.crop(self.crop_size)
                if self.size:
                    img.resize(self.size)
                self.tmp_files.append(img.write_temp())
            frames.append(imageio.imread(img.path))

        progress(i + 1, len(self.images) + 1, 'writing gif: "{}"'.format(self.output_name))
        imageio.mimwrite(self.output_name, frames, format='gif', fps=self.fps)
        progress(10, 10, 'Done writing: {}\n'.format(self.output_name))


def user_confirmation(msg):
    """ user confirmation. simple yes/no question.
    return: user's desicion """

    #  sys.stdout.write(msg)
    choice = str(raw_input(msg).lower())
    if choice.startswith('y'):
        return True
    elif choice.startswith('n'):
        return False
    else:
        sys.stdout.write('respond with \'yes\' or \'no\'\n')
        user_confirmation(msg)

def progress(count, total, msg=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[{}] {}% - {}\r'.format(bar, percents, msg))
    sys.stdout.flush()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output', help='output filename', required=True)
    parser.add_argument('-i', '--input', help='input filename. use * wildcard to find sequence', nargs='+', required=True)
    parser.add_argument('-fps', '--framesPerSecond', help='frames per secons', default=10)
    parser.add_argument('-r', '--resize', help='resize', default='', nargs='+')
    parser.add_argument('-c', '--crop', help='crop', default='', nargs='+')
    parser.add_argument('-s', '--show', help='show gif', action='store_true')

    args = vars(parser.parse_args())
    ctrl= Seq2Gif(args)
    ctrl.run_command()

