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

import errno
import jinja2
import toml
import markdown
import os
import posixpath
import shutil
import re

from functools import partial


def ensure_dir(directory):
  try:
    os.makedirs(directory)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise


def copytree(src, dst, symlinks=False, ignore=None):
  if not os.path.exists(dst):
    os.makedirs(dst)
  for item in os.listdir(src):
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if os.path.isdir(s):
      copytree(s, d, symlinks, ignore)
    else:
      if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
        shutil.copy2(s, d)


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


def pages_from_directory(directory, recursive=True, consider_index=True):
  """
  Creates a list of #Page#s from the Markdown files in *directory*. Page
  details are parsed using #parse_page_details(). If a directory contains
  pages but there is no documentation file for that directory, the details
  are parsed from a `.toml` file with the same name instead.
  """

  pages = {}
  directories = []  # Save directories for later

  for name in os.listdir(directory):
    if not consider_index and name == 'index.md': continue
    path = os.path.join(directory, name)
    if os.path.isdir(path):
      new_path = os.path.join(path, 'index.md')
      if os.path.isfile(new_path):
        directories.append((name, path))
        path = new_path
        name += '.md'

    if name.endswith('.md'):
      name = name[:-3]
      with open(path) as fp:
        content = fp.read()
      content, details = parse_page_details(content, path)
      if details.get('content-from'):
        with open(os.path.join(os.path.dirname(path), details['content-from'])) as fp:
          content = fp.read()
      page = Page(name, content, details)
      pages[page.name] = page
    elif os.path.isdir(path):
      directories.append((name, path))

  if recursive:
    for name, path in directories:
      children = pages_from_directory(path, recursive=True, consider_index=False)
      if children:
        # Get the page that contains these children, or create a page
        # without content (a folder) for them.
        page = pages.get(name)
        if not page:
          # Check if there's a details TOML file for this directory.
          details_fn = path + '.toml'
          if not os.path.isfile(details_fn):
            details_fn = os.path.join(path, 'index.toml')
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

  def __repr__(self):
    return '<Page {!r}>'.format(self.path)

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

  def sort(self):
    def key(p):
      return (p.detail('ordering-priority', 0), p.detail('title', p.name))
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

  def render(self, renderer):
    template = renderer.jinja_env.get_template('page.html')
    return template.render(page=self)


class RootPage(Page):

  def __init__(self, children=None):
    Page.__init__(self, None, None, None)
    if children:
      self.add_child_page(*children)

  def __str__(self):
    return '\n'.join(map(str, self.children))


class JinjaAbsoluteFileLoader(jinja2.BaseLoader):

  def get_source(self, environment, template):
    with open(template) as fp:
      content = fp.read()
    mtime = os.path.getmtime(template)
    def uptodate():
      try:
        return path.getmtime(template) == mtime
      except OSError:
        return False
    return content, template, uptodate


class Renderer(object):
  """
  This class implements rendering all pages in a site.

  # Parameters
  pages (RootPage, or list of Page)
  """

  def __init__(self, pages, config):
    if isinstance(pages, RootPage):
      pages = pages.children
    self.pages = pages
    self.config = config
    self.preprocessors = []
    self.shortcodes = {}
    self.theme_dir = config.get('theme', str(module.directory.joinpath('theme')))
    self.jinja_env = jinja2.Environment(
      loader=jinja2.FileSystemLoader(['theme', self.theme_dir])
    )

    markdown_extensions = config.get('markdown-extensions', ['toc', 'extra', 'codehilite'])
    self.jinja_env.globals.update({
      'renderer': self,
      'config': config,
      'Markdown': lambda: markdown.Markdown(markdown_extensions),
      'url_for': self.url_for,
    })

    self.trailing_slashes = config.get('trailing-slashes', True)
    self.current_page = None

    for preproc in config.get('preprocessors', ['yassg:preprocess']):
      module_name, member = preproc.split(':')
      if module_name == 'yassg':
        plugin = module.namespace
      else:
        plugin = require(module_name, current_dir='.')
      self.preprocessors.append(getattr(plugin, member))

    # Load all shortcodes.
    for directory in [str(module.directory), os.path.join(self.theme_dir), 'theme', '.']:
      script = os.path.join(directory, 'shortcodes.py')
      if os.path.isfile(script):
        script = require(os.path.abspath(script))
        for key, value in vars(script).items():
          if callable(value):
            self.shortcodes[key] = value
      shortcodesdir = os.path.join(directory, 'shortcodes')
      if os.path.isdir(shortcodesdir):
        for name in os.listdir(shortcodesdir):
          if not name.endswith('.html'): continue
          with open(os.path.join(shortcodesdir, name)) as fp:
            template = self.jinja_env.from_string(fp.read())
          self.shortcodes[name[:-5]] = partial(self._render_shortcode_template, template)

  def _render_shortcode_template(self, template):
    return template.render(page=self.current_page)

  def find_page(self, name):
    path = self._absolute_path(name)
    parts = path.split('/')
    if not parts:
      return None
    pages = self.pages
    for part in parts:
      for page in pages:
        if page.name == part:
          pages = page.children
          break
      else:
        page = None
        break
    return page

  def relpath(self, path, is_page=False):
    """
    Returns a relative path from the current_page.
    """

    ref = self._absolute_path(self.current_page.path)
    if not self.trailing_slashes:
      ref = os.path.dirname(ref)
    if not path and not ref:
      return ''
    if not path:
      res = '/'.join(['..'] * (ref.count('/') + 1))
    else:
      res = posixpath.relpath(path, ref)
    if self.trailing_slashes and not res.endswith('/') and is_page:
      res += '/'
    return res

  def url_for(self, path_or_page):
    """
    Returns a relative path to the specified *page* from the current page.
    """

    if isinstance(path_or_page, Page):
      return self.relpath(self._absolute_path(path_or_page.path), is_page=True)
    else:
      return self.relpath(path_or_page)

  def _absolute_path(self, path, file=False):
    parts = path.split('/')
    if self.trailing_slashes and parts[-1] == 'index':
      parts.pop()
    if not self.trailing_slashes:
      parts[-1] += '.html'
    elif file:
      parts.append('index.html')
    return '/'.join(parts)

  def render(self, directory):
    """
    Renders all pages to *directory* and copies the theme's static files.
    """

    # Check if there's any plugin Python files in the themes dir.
    for name in os.listdir(self.theme_dir):
      if name.endswith('.yassg-theme.py'):
        extension = require(os.path.join(self.theme_dir, name))
        extension.before_render(self)

    def recursion(page):
      self.current_page = page
      filename = os.path.join(directory, self._absolute_path(page.path, file=True))
      ensure_dir(os.path.dirname(filename))
      if page.content:
        print('writing', filename)
        # Preprocess the page content.
        for preproc in self.preprocessors:
          preproc(self, page)

        with open(filename, 'w') as fp:
          fp.write(page.render(self))
      [recursion(child) for child in page.children]

    ensure_dir(directory)
    [recursion(page) for page in self.pages]

    dest_dir = os.path.join(directory, 'static')
    static_dirs = [os.path.join(self.theme_dir, 'static'), 'theme/static']
    for static_dir in static_dirs:
      if os.path.isdir(static_dir):
        print('copying from', static_dir, 'to', dest_dir)
        copytree(static_dir, dest_dir)


def preprocess(renderer, page):
  """
  Yassg Markdown preprocessor.
  """

  def sub_ref(m):
    if m.group().startswith('\\'):
      return m.group()[1:]
    text, ref = m.groups()
    if not ref:
      text, ref = None, text
    page = renderer.find_page(ref)
    if not page:
      return m.group()
    if not text:
      text = page.detail('title', page.name)
    return '<a href="{}">{}</a>'.format(renderer.url_for(page), text)

  page.content = re.sub(r'\\?\[\[(.*?)\]\](?:\((.*?)\))?', sub_ref, page.content)

  def sub_shortcode(m):
    if m.group().startswith('\\'):
      return m.group()[1:]
    call = m.group(1)
    return str(eval(call, renderer.shortcodes))

  page.content = re.sub(r'\\?\{\{\s*(\w+\(.*?)\w*\s*\}\}', sub_shortcode, page.content, re.M)
