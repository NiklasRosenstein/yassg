# Yet another static site generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-green.svg)](http://niklasrosenstein.github.io/yassg/)

Yassg is yet another static site generator that is built with [Node.py]
on Python 3, based on Jinja2 and Markdown.

[Node.py]: https://nodepy.org/

__Features__

* Powerful theming with Jinja2 and Python plugins
* Generates relative URLs to other pages

__Installation__

    $ pip3 install node.py
    $ nppm3 install -g git+https://github.com/NiklasRosenstein/yassg.git
    $ yassg --help
    Usage: yassg [OPTIONS]

    Yet another static site generator.

    Options:
    -C, --config TEXT  Configuration file. Defaults to .yassg.toml
    --help             Show this message and exit.

__Configuration__: `.yassg.toml`

```python
# Build related (defaults shown)
docs-dir = "docs"
build-dir = ".build/docs"
recursive = true
trailing-slashes = true

# Content rendering related (defaults shown)
theme = "path/to/theme"
markdown-extensions = ["extra", "codehilite"]
site-name = "This is my page title"
footer-notice = "Copyright &copy; 2017 My Name"

# Theme features
disqus-shortname = "..."
google-analytics = "..."
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
