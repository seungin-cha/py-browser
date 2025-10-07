import re
import socket
import ssl
import sys
import tkinter
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
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        body = response.read(int(response_headers.get("content-length", 0)))
        s.close()

        return body


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
        text = re.sub(r"<[^>]*>", "", body).strip()
        return text

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            self.canvas.create_text(x, y - self.scroll, text=c)

    def load(self, url: URL):
        body = url.request()
        text = self.lex(body)
        self.display_list = layout(text)
        self.draw()


def layout(text: str):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x > WIN_WIDTH - HSTEP:
            cursor_x = HSTEP
            cursor_y += VSTEP
    return display_list


if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
