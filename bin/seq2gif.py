#!/usr/bin/python

import os
import sys
import glob
import imageio
import tempfile
import argparse
import PIL.Image as pil


class Seq2Gif(object):
    """ Seq2Gif - convert image sequence to gif.
    init with arguments defined by argparser. input and output will be validated

    Args:
        args (dict):
            input (list of string): input image sequence or path with wildcard (* or ?)
            output (string): path where the gif will be wirtten
            framesPerSecond (int): you got it
            size (list of 4 int): crop and/resize output
    """

    def __init__(self, args):

        self.images = self.validate_input(args['input'])
        self.output_name = self.validate_output(args['output'])
        self.fps = float(args['framesPerSecond'])
        self.size = self.validate_size(args['resize'])
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
                    sys.stderr.write('Could not find a valid image sequence')
                else:
                    return images
            else:
                sys.stderr.write('Not enough input. Only one image given. Use "*" as wildcard to detect an image sequence')
        else:
            for img in images:
                if not os.path.isfile(img):
                    sys.stderr.write('File does not exist: {}'.format(img))
                    return
            return images

    def validate_output(self, output_name):
        """ validate out path. """

        output_name = os.path.realpath(os.path.expanduser(output_name)).strip()
        if os.path.isfile(output_name):
            if not user_confirmation('File already exists: {}\nOverwrite? (y)es/(n)o?\n>> '.format(output_name)):
                sys.stdout.write('Aborted by user\n')
                return
        elif os.path.isdir(output_name):
            sys.stdout.write('Output argument must be a file not directory')
            return
        elif not os.path.isdir(os.path.dirname(output_name)):
            sys.stdout.write('Output directory "{}" does not exist\n'.format(os.path.dirname(output_name)))
            return
        elif os.path.splitext(output_name)[-1] != '.gif':
            path, ext = os.path.splitext(output_name)
            output_name = '{}.gif'.format(path)

        return output_name

    def validate_size(self, size):
        """ validate resize argument.
        return size if input was valid else None """

        def int_float(val):
            return float(int(val))

        if size:
            valid = True
            try:
                size = map(int_float, size)
                if len(size) != 4:
                    valid = False
            except ValueError:
                valid = False

            if not valid:
                sys.stderr.write('Invalid argument --size int(x) int(y) int(h) int(w)')
                return

        return size

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
            img = os.path.realpath(os.path.expanduser(img))

            if self.size:
                size = [float(s) for s in self.size]
                img = self.resize(img, *size)

            progress(i, len(self.images) + 1, 'reading image: {}'.format(os.path.basename(img)))
            frames.append(imageio.imread(img))

        progress(i + 1, len(self.images) + 1, 'writing gif: {}'.format(self.output_name))
        imageio.mimwrite(self.output_name, frames, format='gif', fps=self.fps)
        progress(10, 10, 'Done writing: {}\n'.format(self.output_name))

    def resize(self, image, pos_x, pos_y, width, height):
        """ resize the given image.
        return name of the new resized temp file """

        if pos_x < pos_x + width and pos_y < pos_y + height:
            tmp_dir = tempfile.gettempdir()

            tmp_name = list(os.path.splitext(os.path.basename(image)))
            tmp_name.insert(1, '_tmp')
            tmp_name = os.path.join(tmp_dir, ''.join(tmp_name))
            self.tmp_files.append(tmp_name)

            image = pil.open(image)
            cropped_img = image.crop((pos_x, pos_y, pos_x + width, pos_y + height))
            cropped_img.save(tmp_name)

            image.close()
            cropped_img.close()

            return tmp_name

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
    parser.add_argument('-s', '--show', help='show gif', action='store_true')

    args = vars(parser.parse_args())
    ctrl= Seq2Gif(args)
    ctrl.run_command()

