# seq2gif

Simple command line tool to convert an image sequence to gif.


# Install

```
git clone https://github.com/wiremas/seq2gif.git
cd seq2gif/
python setup.py
```

# Options

```
-i --input					sequence of input image pathes or a single path with a wildcard (* or ?)
-o --output					path to the resulting .gif image
-fps --framesPerSecond		playback speed for the gif.
-r --resize					resize the resuting gif. the agrument can be formatted as follows:
							1. string ending with "%" indicates to scale by the given percetage.
							2. single int defines the width. the height will be scaled proportionally.
							3. two ints define width and height.
-c --crop					crop the input image. the argument can be formatted as follows:
							1. two ints define the crop size (width/height) from the top left corner.
							2. four ints define the top left corner and the crop size.
-s --show					show the resulting .gif
```

# Usage example

Get img01.png and img02.png and write to out.gif
```
seq2gif -i ~/Desktop/img01.png ~/Desktop/img02.png -o "~/Desktop/out.gif"
```

Get all *.png files, crop, resize and write gif with 10fps. Finally show the resulting gif.
```
seq2gif -i "~/Desktop/*.png" -o "~/Desktop/out.gif" -fps 10 -size 0 50 100 200 -s
```