+++
title = "Usage"
ordering-priority = 5
+++

[Node.py]: https://nodepy.org/
[Git worktree]: https://git-scm.com/docs/git-worktree
[TOML]: https://github.com/toml-lang/toml

## Installation

Yassg is built is built with [Node.py] and Python 3. To install Node.py,
install it just like any other Python module via Pip.

    $ pip3 install node.py

Then you can install Yassg with the Node.py's package manager **nppm**.

    $ nppm3 install -g git+https://github.com/NiklasRosenstein/yassg.git

## Command-line Interface

Invoking Yassg will builds the full documentation. When you set up the build
directory as a [Git worktree], you can use the `--commit` or `--push` options
to automatically update the GitHub pages branch.

    $ yassg --help
    Usage: yassg [OPTIONS]

    Yet another static site generator.

    Options:
    -C, --config TEXT  Configuration file. Defaults to .yassg.toml
    --commit           Create a new commit after the build. Use only when the
                       build directory is set-up as a git worktree.
    --push             Commit and push after the build. Use only when the build
                       directory is set-up as a git worktree.
    --help             Show this message and exit.

## Configuration

The configuration file is `.yassg.toml` and  is read from the current working
directory. All paths defined in the configuration file are also considered
relative to the working directory. The configuration file format is [TOML].

Example:

    site-name = "My site"
    footer-notice = "Copyright &copy; 2017 John Cena"
    trailing-slashes = true
    disqus-shortname = "mysite-com"
    google-analytics = "UA-324242343-1"

__docs-dir__

The directory where the markdown source files reside. The default value for
this option is `"docs/"`.

__build-dir__

The build output directory. The default value is `".build/docs"`.

__recursive__

Search for pages in the **docs-dir** recursively. The default is `true`.

__trailing-slashes__

Put every output HTML file into its own directory, causing the site to be
served with trailing slashes rather than `.html` filenames in the URL.

__theme__

Path to a theme directory. The default theme is used if no path is specified
in the configuration. Check out the [Theming](../theming) documentation for
more information on themes.

__markdown-extensions__

A list of markdown extensions to use for the Python `markdown` library.
Defaults to `["toc", "extra", "codehilite"]`.

__site-name__

Themes commonly use this configuration parameter for the site name.

__footer-notice__

Themes commonly use this configuration parameter in the footer.

__disqus-shortname__

Themes commonly use this configuration parameter for Disqus support.

__google-analytics__

Themes commonly use this configuration parameter for Google Analytics support.

__github-repository__

Themes commonly use this configuration parameter to include a link to a GitHub
repository.

## Directory layout

Yassg will create a page for every markdown file in the **docs-dir**. If
the **recursive** option is enabled, sub-directories will be checked as well.
A sub-directory that contains markdown files may also have a markdown source
file with the same name.

Alternatively, you can add a `.toml` file with the same name to specify page
options (most importantly, the **ordering-priority** and **title**) for the
navigation rendering.

    docs/
      index.md
      cli.md
      cli/
        bin.md
        package.md
      examples.toml
      examples/
        example1.md
        example2.md

## Page configuration

Pages can be configured with a special TOML section at the beginning of the
file enclosed by triple pluses (`+++`).

Example:

    +++
    title = "Home"
    ordering-priority = 10
    render-title = false
    content-from = "../README.md"
    +++

__title__

The page's title. Themes can read the page's display name using

```python
page.detail('title', default=page.name)
```

__ordering-priority__

A number that specifies the ordering priority. Higher priority causes the
page to appear earlier in the list. Pages with the same priority will be
sorted alphabetically. The default value is `0`.

__render-title__

Render the title of the page. The default value is `true`.

__content-from__

Read the content of this page from a different file. This is useful if you
wnat to include the `README.md` of your repository in your site without
duplicating its content.
