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

import click
import toml
import os
import yassg from './yassg.py'

@click.command()
@click.option('-C', '--config', default='.yassg.toml')
def main(config):
  with open(config) as fp:
    config = toml.load(fp)

  docs_dir = config.get('docs-dir', 'docs')
  build_dir = config.get('build-dir', '.build/docs')
  recursive = config.get('recursive', True)
  theme = config.get('theme', os.path.join(__directory__, 'theme'))
  trailing_slashes = config.get('trailing-slashes', False)
  markdown_extensions = config.get('markdown-extensions', ['extra', 'codehilite'])

  root = yassg.RootPage(yassg.pages_from_directory(docs_dir, recursive=recursive))
  root.sort()

  yassg.render_to_directory(
    root, build_dir, config, theme,
    trailing_slashes=trailing_slashes,
    markdown_factory=yassg.new_markdown_factory(markdown_extensions)
  )

if require.main == module:
  main()
