import re
import socket
import ssl
import sys
import tkinter
from urllib.parse import urlparse


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
        self.canvas = tkinter.Canvas(self.window, width=800, height=600)
        self.canvas.pack()

    def load(self, url: URL):
        body = url.request()

        self.canvas.create_rectangle(10, 20, 400, 300)
        self.canvas.create_oval(100, 100, 150, 150)
        self.canvas.create_text(200, 150, text="Hi!")


if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
