# PrintPDF

A tool to print a web page to PDF
Uses FireFox to do all the hard work.

### Installation
```
git clone https://github.com/reinhrst/svg2png
git co printpdf
```
Alternatively, just download the `main.py` file from this repo/branch.

The path to FireFox is set up for MacOs; if you have something else, you need to change this in `main.py`.

This tool uses Firefox (though Marionette scripting) to convert SVG files to PNG.
There are other tools out there to do a conversion, however in my experience, most tools have pretty lousy SVG support, especially when the going gets tough.


### Usage
```
python main.py https://www.vive.com/uk/product/vive-focus3/overview/ /tmp/out.pdf
```

