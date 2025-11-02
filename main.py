import re
import socket
import ssl
import sys
import tkinter
import tkinter.font
from urllib.parse import urlparse

WIN_WIDTH, WIN_HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100


class URL:
    def __init__(self, url: str):
        parsed_url = urlparse(url)
        self.scheme = parsed_url.scheme
        assert self.scheme in ["http", "https"]
        self.host = parsed_url.hostname
        self.path = parsed_url.path
        self.port = parsed_url.port or 443 if self.scheme == "https" else 80

    def request(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        s.connect((self.host, self.port))

        request = f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += "\r\n"
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        status_line = response.readline()
        version, status, explanation = status_line.split(" ", 2)
        response_headers = {}
        while True:
            line = response.readline()
            if line in ("\r\n", "\n", ""):
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        body = response.read(int(response_headers.get("content-length", 0)))
        s.close()

        return body


class Text:
    def __init__(self, text: str):
        self.text = text


class Tag:
    def __init__(self, tag: str):
        self.tag = tag


class Layout:
    def __init__(self, tokens):
        self.display_list = []
        self.line = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.size = 12
        self.slant = "roman"
        self.weight = "normal"

        for token in tokens:
            self.process(token)
        self.flush()

    def process(self, token):
        if isinstance(token, Text):
            for word in token.text.split():
                font = tkinter.font.Font(size=16, slant=self.slant, weight=self.weight)
                w = font.measure(word)
                if self.cursor_x + w > WIN_WIDTH - HSTEP:
                    self.flush()
                self.line.append((self.cursor_x, word, font))
                self.cursor_x += w + font.measure(" ")
        elif isinstance(token, Tag):
            match token.tag:
                case "small":
                    self.size -= 2
                case "/small":
                    self.size += 2
                case "big":
                    self.size += 4
                case "/big":
                    self.size -= 4
                case "i":
                    self.slant = "italic"
                case "/i":
                    self.slant = "roman"
                case "b":
                    self.weight = "bold"
                case "/b":
                    self.weight = "normal"
                case "br":
                    self.flush()
                case "/p":
                    self.flush()
                    self.cursor_y += VSTEP

    def flush(self):
        if not self.line:
            return

        # Calculate baseline for the current line
        metrics = [font.metrics() for _, _, font in self.line]
        max_ascent = max(m["ascent"] for m in metrics)
        baseline = self.cursor_y + 1.25 * max_ascent

        # Add words to display list with adjusted y position
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        # Clear the current line and update cursor positions
        max_descent = max(m["descent"] for m in metrics)
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIN_WIDTH, height=WIN_HEIGHT)
        self.canvas.pack()
        self.scroll = 0

        self.window.bind("<Down>", self.scroll_down)

    def scroll_down(self, event):
        self.scroll += SCROLL_STEP
        self.draw()

    def lex(self, body: str):
        out = []
        buffer = ""
        in_tag = False
        for c in body:
            if c == "<":
                in_tag = True
                if buffer:
                    out.append(Text(buffer))
                buffer = ""
            elif c == ">":
                in_tag = False
                out.append(Tag(buffer))
                buffer = ""
            else:
                buffer += c
        if not in_tag and buffer:
            out.append(Text(buffer))
        return out

    def draw(self):
        self.canvas.delete("all")
        for x, y, word, font in self.display_list:
            if -VSTEP < y - self.scroll <= WIN_HEIGHT:
                self.canvas.create_text(
                    x, y - self.scroll, text=word, font=font, anchor="nw"
                )

    def load(self, url: URL):
        body = url.request()
        tokens = self.lex(body)
        self.display_list = Layout(tokens).display_list
        self.draw()


if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
