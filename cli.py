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
import subprocess
import yassg from './yassg.py'

@click.command()
@click.argument('build_dir', default='build')
@click.option('-C', '--config', default='yassg.toml',
  help='Configuration file. Defaults to "yassg.toml"')
@click.option('--commit', is_flag=True,
  help='Create a new commit after the build. Use only when the build '
    'directory is set-up as a git worktree.')
@click.option('--push', is_flag=True,
  help='Commit and push after the build. Use only when the build '
    'directory is set-up as a git worktree.')
def main(build_dir, config, commit, push):
  """
  Yet another static site generator.
  """

  with open(config) as fp:
    config = toml.load(fp)

  root = yassg.RootPage(yassg.pages_from_directory('content', recursive=True))
  root.sort()

  renderer = yassg.Renderer(root, config)
  renderer.render(build_dir)

  if commit or push:
    print('Creating new commit in "{}" ...'.format(build_dir))
    subprocess.call(['git', 'add', '.'], cwd=build_dir)
    subprocess.call(['git', 'commit', '-m', 'Update'], cwd=build_dir)
  if push:
    print('Pushing to "{}" ...'.format(build_dir))
    subprocess.call(['git', 'push', 'origin', 'gh-pages'], cwd=build_dir)

if require.main == module:
  main()
