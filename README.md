# Yet another statis site generator.

Yassg is yet another static site generator that is built with [Node.py]
on Python 3, based on Jinja2 and Markdown.

[Node.py]: https://nodepy.org/

__Installation__

    $ pip3 install node.py
    $ nppm3 install -g git+https://github.com/NiklasRosenstein/yassg.git
    $ yassg

__Configuration__: `.yassg.toml`

```toml
docs-dir = "docs"                   # default
build-dir = ".build/docs"           # default
recursive = true                    # default
trailing-slashes = false            # default
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
