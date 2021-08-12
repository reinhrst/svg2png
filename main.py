import argparse
import base64
import json
import logging
import os
import pathlib
import re
import socket
import subprocess
import tempfile
import threading
import time

logger = logging.getLogger()

CODE_COMMAND = 0
CODE_RESPONSE = 1
FIREFOX_BIN = os.environ.get(
    "FIREFOX_BIN", "/Applications/Firefox.app/Contents/MacOS/firefox-bin")
MARIONETTE_PORT_REGEX = re.compile(
    r'''^user_pref\("marionette.port", (\d+)\);$''', re.MULTILINE)


class MarionetteException(Exception):
    def __init__(self, error):
        self.error = error
        super().__init__("MarionetteException: %r", error)


class MarionetteConnection:
    def __init__(self, host, port):
        self.message_id = 0
        self.unprocessed_data: bytes = b""
        logger.info("Connecting")
        self.s = socket.create_connection((host, port))
        logger.info("Connection established")
        handshake = self.receive(handshake=True)
        if handshake["applicationType"] != "gecko":
            raise Exception(
                "Expected application to be gecko, not " + handshake["application"])
        if handshake["marionetteProtocol"] != 3:
            raise Exception(
                "Expected marionetteProtocol to be 3, not " + str(
                    handshake["marionetteProtocol"]))
        self.newSession()

    def receive(self, handshake=False):
        while True:
            self.unprocessed_data += self.s.recv(4096)
            colonpos = self.unprocessed_data.index(b":")
            if colonpos != -1:
                messagelength = int(self.unprocessed_data[:colonpos].decode("utf-8"))
                messageend = colonpos + 1 + messagelength
                if len(self.unprocessed_data) >= messageend:
                    fullmessage = self.unprocessed_data[:messageend]
                    logger.debug("Received %r", fullmessage)

                    self.unprocessed_data = self.unprocessed_data[messageend:]
                    message = fullmessage[colonpos + 1:]
                    if handshake:
                        return json.loads(message)
                    code, _messageId, error, reply = json.loads(message)
                    assert code == CODE_RESPONSE
                    if error is not None:
                        raise MarionetteException(error)
                    return reply

    def send(self, command, arguments):
        marionette_message = [CODE_COMMAND, self.message_id, command, arguments]
        jsonmessage = json.dumps(marionette_message).encode("utf-8")
        fullmessage = b"%d:%b" % (len(jsonmessage), jsonmessage)
        logger.debug("Sending %r", fullmessage)
        try:
            self.s.sendall(fullmessage)
            return self.receive()
        finally:
            self.message_id += 1

    def newSession(self):
        reply = self.send("WebDriver:NewSession", {})
        self.session_id = reply["sessionId"]


    def navigateTo(self, path_or_url: str):
        self.send("WebDriver:Navigate", {"url": path_or_url})

    def executeJavascript(self, javascript: str):
        self.send("WebDriver:ExecuteScript", {"script": javascript, "args": []})


    def findElementIdByCssSelector(self, selector: str):
        result = self.send(
            "WebDriver:FindElements",{"using":"css selector","value":selector})
        return list(result[0].values())[0]

    def takeScreenshotFromElement(self, element_id, output_png_filename):
        result = self.send("WebDriver:TakeScreenshot",
                           {"full": False, "highlights": [], "id": element_id})
        pngdata = base64.b64decode(result["value"])
        pathlib.Path(output_png_filename).write_bytes(pngdata)
        logger.info("Written: %s, %d bytes", output_png_filename, len(pngdata))
        logger.info("%s", subprocess.check_output(["file", output_png_filename]))

    def end(self):
        self.send("Marionette:Quit", {"flags": ["eForceQuit"]})
        assert self.s.recv(4096) == b""
        logger.info("connection closed")

def read_and_log_prefixed(fd, prefix):
    while True:
        line = fd.readline()
        if line == b"":
            break
        logger.info("%s%s", prefix, line)


def run(args):
    with tempfile.TemporaryDirectory() as profiledir:
        profiledir = tempfile.mkdtemp()
        prefs = (pathlib.Path(profiledir) / "prefs.js")
        prefs.write_text(
            '''user_pref("marionette.port", 0);\n''')
        firefox = subprocess.Popen(
            [
                FIREFOX_BIN,
                "--marionette",
                "--headless",
                "--no-remote",
                "--profile", profiledir
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        threading.Thread(target=read_and_log_prefixed,
                         args=(firefox.stdout, "FIREFOX STDOUT> ")).start()
        threading.Thread(target=read_and_log_prefixed,
                         args=(firefox.stderr, "FIREFOX STDERR> ")).start()

        try:
            while True:
                time.sleep(0.1)
                match = MARIONETTE_PORT_REGEX.search(prefs.read_text())
                if match:
                    port = int(match.group(1))
                if port != 0:
                    break
            conn = MarionetteConnection("127.0.0.1", port)
            conn.navigateTo(args.input_url)
            if args.width:
                conn.executeJavascript(
                    'document.querySelector(":root").style.width = %r' % args.width)
            if args.height:
                conn.executeJavascript(
                    'document.querySelector(":root").style.height = %r' % args.height)
            if args.javascript:
                conn.executeJavascript(args.javascript)
            element_id = conn.findElementIdByCssSelector(":root")
            conn.takeScreenshotFromElement(element_id, args.output_png_filename)
            conn.end()
            try:
                logger.info("waiting for firefox to quit")
                firefox.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Firefox did not close within reasonable time")

        finally:
            if firefox.poll() is None:
                logger.warning("killig a Fire Fox")
                firefox.terminate()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--help", action="help")
    parser.add_argument("--width", "-w",
                        help="Set the width of the root element through CSS.")
    parser.add_argument("--height", "-h",
                        help="Set the height of the root element through CSS.")
    parser.add_argument("--javascript", "--js", help="Execute javascript.")
    parser.add_argument("input_url")
    parser.add_argument("output_png_filename")
    run(parser.parse_args())

    logger.info("done")
