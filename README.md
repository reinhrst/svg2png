# PrintPDF

A tool to print a web page to PDF
Uses FireFox to do all the hard work.

Read [this blog post](https://blog.claude.nl/tech/converting-svg-into-png/) for the process, and more info.

### Note - known bug
There is [a known issue on the FireFox side](https://github.com/mozilla/geckodriver/issues/1905) that printing of PDFs that are more than 500kB large will result in an error:
```
Traceback (most recent call last):
  File "main.py", line 178, in <module>
    run(parser.parse_args())
  File "main.py", line 157, in run
    conn.printToPdf(args.output_pdf_filename)
  File "main.py", line 102, in printToPdf
    result = self.send(
  File "main.py", line 75, in send
    return self.receive()
  File "main.py", line 65, in receive
    raise MarionetteException(error)
__main__.MarionetteException: ('MarionetteException: %r', {'error': 'unknown error', 'message': 'RangeError: too many arguments provided for a function call', 'stacktrace': 'GeckoDriver.prototype.print@chrome://remote/content/marionette/driver.js:3025:37\n'})
```

There [seems to be a fix that should be included in Firefox 93](https://bugzilla.mozilla.org/show_bug.cgi?id=1719124), which is due for release [in October 2021](https://wiki.mozilla.org/Release_Management/Calendar).
If you cannot wait, use `-f Dockerfile.firefox-nightly` in your `docker build` command.

### Installation
```
git clone https://github.com/reinhrst/svg2png
git co printpdf
```
Alternatively, just download the `main.py` file from this repo/branch.

The path to FireFox is set up for MacOs; if you have something else, you need to change this in `main.py`, or put the path to the executable in the `FIREFOX_BIN` environment variable.

This tool uses Firefox (though Marionette scripting) to convert SVG files to PNG.
There are other tools out there to do a conversion, however in my experience, most tools have pretty lousy SVG support, especially when the going gets tough.


### Usage
```
python main.py https://blog.claude.nl/tech/using-a-go-library-fzf-lib-in-the-browser/ /tmp/out.pdf
```

You can add arbitrary JavaScript by using the `--javascript` commandline option.

## Running through Docker
To run the tool in Docker, do:
```
git clone https://github.com/reinhrst/svg2png
cd svg2png
git co printpdf
docker build -t printpdf .
mkdir /tmp/data
docker run -v /tmp/data:/data printpdf https://blog.claude.nl/tech/using-a-go-library-fzf-lib-in-the-browser/ /data/blog.pdf
open /tmp/data/blog.pdf
```

Note that the code above may break if the PDF file is more than 500kB; see the "Known bug" above for a fix.
