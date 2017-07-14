# Copyright (c) 2017  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
A light-weight alternative over MkDocs.
"""

import errno
import jinja2
import toml
import markdown
import os
import posixpath
import shutil
import re


def load_page_details(data, filename=None):
  """
  # Raises
  ValueError of (filename, error)
  """

  try:
    options = toml.loads(data)
  except toml.TomlDecodeError as exc:
    raise ValueError(filename, exc)
  if not isinstance(options, dict):
    raise ValueError(filename, 'page details could not be parsed into a JSON object')
  return options


def parse_page_details(content, filename=None):
  """
  Parses the "details" section at the top of a page which is enclosed in
  triple plus-signs and formatted in TOML format. For example:

      +++
      title = "Home"
      ordering-priority = 10
      +++

  # Returns
  tuple of (content, dict)

  # Raises
  ValueError of (filename, error)
  """

  match = re.match('\s*\+\+\+(.*?)\+\+\+', content, re.M | re.S)
  if not match:
    return content, {}

  content = content[match.end():]
  options = load_page_details(match.group(1), filename)
  return content, options


def pages_from_directory(directory, recursive=True):
  """
  Creates a list of #Page#s from the Markdown files in *directory*. Page
  details are parsed using #parse_page_details(). If a directory contains
  pages but there is no documentation file for that directory, the details
  are parsed from a `.toml` file with the same name instead.
  """

  pages = {}
  directories = []  # Save directories for later

  for name in os.listdir(directory):
    path = os.path.join(directory, name)
    if name.endswith('.md'):
      name = name[:-3]
      with open(path) as fp:
        content = fp.read()
      content, details = parse_page_details(content, path)
      if details.get('content-from'):
        with open(os.path.join(directory, details['content-from'])) as fp:
          content = fp.read()
      page = Page(name, content, details)
      pages[page.name] = page
    elif os.path.isdir(path):
      directories.append((name, path))

  if recursive:
    for name, path in directories:
      children = pages_from_directory(path, recursive=True)
      if children:
        # Get the page that contains these children, or create a page
        # without content (a folder) for them.
        page = pages.get(name)
        if not page:
          # Check if there's a details TOML file for this directory.
          details_fn = path + '.toml'
          if os.path.isfile(details_fn):
            with open(details_fn) as fp:
              details = load_page_details(fp.read(), details_fn)
          else:
            details = None
          page = Page(name, None, details)
          pages[name] = page

        page.add_child_page(*children)

  return list(pages.values())


class Page(object):
  """
  A page may have content or subpages, or both.
  """

  def __init__(self, name, content, details):
    self.parent = None
    self.name = name
    self.content = content
    self.details = {} if details is None else details
    self.children = []

  def __str__(self):
    parts = ['* {}'.format(self.detail('title', self.name))]
    for child in self.children:
      for line in str(child).split('\n'):
        parts.append('  ' + line)
    return '\n'.join(parts)

  def __getitem__(self, key):
    return self.details[key]

  def detail(self, key, default=None):
    return self.details.get(key, default)

  def add_child_page(self, *pages):
    for page in pages:
      if not isinstance(page, Page):
        raise TypeError('expected Page object')
      if page.parent is not None:
        raise ValueError('page already has a parent')
      page.parent = self
      self.children.append(page)

  def remove(self):
    if self.parent:
      self.parent.children.remove(self)
      self.parent = None

  def relpath(self, relative_to_page):
    if not isinstance(relative_to_page, Page):
      raise TypeError('expected Page object')
    return posixpath.relpath(self.path, posixpath.dirname(relative_to_page.path))

  def sort(self):
    def key(p):
      return (-p.detail('ordering-priority', 0), p.detail('title', p.name))
    self.children.sort(key=key)
    for child in self.children:
      child.sort()

  @property
  def path(self):
    parts = []
    while self and self.name is not None:
      parts.append(self.name)
      self = self.parent
    return '/'.join(reversed(parts))

  @property
  def root(self):
    while self.parent:
      self = self.parent
    return self

  def render(self, jinja_env):
    template = jinja_env.get_template('page.html')
    return template.render(page=self)


class RootPage(Page):

  def __init__(self, children=None):
    Page.__init__(self, None, None, None)
    if children:
      self.add_child_page(*children)

  def __str__(self):
    return '\n'.join(map(str, self.children))


def new_markdown_factory(*args, **kwargs):
  return lambda: markdown.Markdown(*args, **kwargs)


def render_to_directory(pages, directory, config, theme_dir,
                        markdown_factory, trailing_slashes=True):
  """
  Renders *pages* to the output *directory*. If *trailing_slashes* is #True,
  every rendered page will be wrapped in a directory. If no *theme_dir* is
  specified, the standard theme of Yassg is used.
  """

  if isinstance(pages, RootPage):
    pages = pages.children
  if config is None:
    config = {}
  if theme_dir is None:
    theme_dir = os.path.join(__directory__, 'theme')

  def ensure_dir(directory):
    try:
      os.makedirs(directory)
    except OSError as e:
      if e.errno != errno.EEXIST:
        raise

  def abs(page, path):
    return posixpath.relpath(path, os.path.dirname(page.path))

  jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(theme_dir)
  )
  jinja_env.globals['config'] = config
  jinja_env.globals['Markdown'] = markdown_factory
  jinja_env.globals['abs'] = abs

  for name in os.listdir(theme_dir):
    if name.endswith('.yassg-theme.py'):
      extension = require('./' + name, current_dir=theme_dir)
      extension.before_render(pages, jinja_env, config)

  def render(page):
    if trailing_slashes:
      filename = os.path.join(directory, page.path, 'index.html')
    else:
      filename = os.path.join(directory, page.path + '.html')
    ensure_dir(os.path.dirname(filename))
    if page.content:
      print('writing', filename)
      with open(filename, 'w') as fp:
        fp.write(page.render(jinja_env))
    [render(child) for child in page.children]

  ensure_dir(directory)
  [render(page) for page in pages]

  static_dir = os.path.join(theme_dir, 'static')
  dest_dir = os.path.join(directory, 'static')
  if os.path.isdir(dest_dir):
    print('removing old', dest_dir)
    shutil.rmtree(dest_dir)
  if os.path.isdir(static_dir):
    print('copying files to', dest_dir)
    shutil.copytree(static_dir, dest_dir)
