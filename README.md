# Yet another statis site generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


Yassg is yet another static site generator that is built with [Node.py]
on Python 3, based on Jinja2 and Markdown.

[Node.py]: https://nodepy.org/

__Features__

* Theming support with Jinja2
* Generates relative URLs to other pages

__Installation__

    $ pip3 install node.py
    $ nppm3 install -g git+https://github.com/NiklasRosenstein/yassg.git
    $ yassg

__Configuration__: `.yassg.toml`

```python
docs-dir = "docs"                                # default
build-dir = ".build/docs"                        # default
recursive = true                                 # default
trailing-slashes = false                         # default
markdown-extensions = ["extra", "codehilite"]    # default
theme = "path/to/theme"                          # default theme included
site-name = "This is my page title"
footer-notice = "Copyright &copy; 2017 My Name"
```

__Directory Layout__

    docs/
      index.md
      cli.md
      cli/
        bin.md
        package.md

__Page-level configuration__

    +++
    title = "Home"
    ordering-priority = 10
    render-title = false
    content-from = "../README.md"
    +++
