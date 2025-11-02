# py-browser
A minimal browser built with Python as a learning project.

## Prerequisites

Ubuntu/Debian:
```bash
# Install Python and Tkinter
sudo apt update
sudo apt install python-is-python3 python3-tk
```

## Running the browser

Run the browser by providing a URL as an argument:
```bash
python main.py http://www.example.com/index.html
```

Example: test mixed font sizes (loads a small HTML example from the Browser Engineering book):
```bash
python main.py https://raw.githubusercontent.com/browserengineering/book/refs/heads/main/www/examples/example3-sizes.html
```

Notes:
- The program supports both HTTP and HTTPS URLs.
- Network access is required to fetch remote pages.

## Features

- Basic HTTP/HTTPS request handling
- Simple HTML lexing into Text/Tag tokens
- Basic HTML styling: <b>, <i>, <small>, <big>
- Line-based layout with baseline alignment to support mixed font sizes
- Font caching using Label-backed Font objects for improved metrics performance
- Support for <br> and </p> for explicit line breaks
- Text rendering with Tkinter Canvas
- Scrolling with Down arrow key
