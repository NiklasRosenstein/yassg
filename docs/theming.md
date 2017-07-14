+++
title = "Theming"
+++

## Theme Structure

A theme must provide a `page.html` template that will then be rendered using
Jinja2. It may also contain other template files that it can include or extend,
but only the `page.html` will be rendered by default.

All files in a theme's `static/` directory will be copied as-is to the output
build directory.

### `before_render(pages, config, jinja_env)`

A theme directory may also contain a Node.py source file suffixed with
`.yassg-theme.py` that will be loaded before the theme is rendered. This
function is called to allow pre-processing of the *jinja_env* and *config*.

## Available Built-ins

### `abs(page, path)`

Returns a relative URL pointing to the specified *path* relative to the
*page* currently being rendered. This is useful to include static files like
CSS and JavaScript from a theme.
