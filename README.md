# seq2gif

Simple command line tool to convert an image sequence to gif.


# Install

```
git clone https://github.com/wiremas/seq2gif.git
cd seq2gif/
python setup.py
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