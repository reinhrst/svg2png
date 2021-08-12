# SVG2PNG

A tool to convert SVG (or any other component that a browser can show) into a PNG.
Uses FireFox to do all the hard work.

### Installation
```
git clone https://github.com/reinhrst/svg2png
```
Alternatively, just download the `main.py` file from this repo.

The path to FireFox is set up for MacOs; if you have something else, you need to change this in `main.py`.

This tool uses Firefox (though Marionette scripting) to convert SVG files to PNG.
There are other tools out there to do a conversion, however in my experience, most tools have pretty lousy SVG support, especially when the going gets tough.

Included in this repo is an SVG file.
At this moment (summer 2021), only Firefox renders this file correctly (not Chrome, not Safari, not Pixelmator Pro, not Inkscape).
So I needed to make sure that the conversion to PNG happens by Firefox.

Firefox is run headless.
This means that the size of the PNG is the size is pixels of the SVG/HTML element (note that if you define an SVG with a width/height as numbers, or with only a viewBox, these numbers are points (`pt`) and each point is 1.333333px.
If you run Firefox non-headless on a retina display, the output PNG is 2 pixels for each `px` size of the element.
So best only use non-headless for debugging.

### Usage
```
python main.py -w 1000px -h auto "file://$(pwd)/example.svg" /tmp/out.png
```

Sets the width css property to `1000px`, and the height to `auto`.
You can add arbitrary JavaScript by using the `--javascript` commandline option.
