+++
title = "Theming"
+++

## Theme Structure

A theme must provide a `page.html` template that will then be rendered using
Jinja2. It may also contain other template files that it can include or extend,
but only the `page.html` will be rendered by default.

All files in a theme's `static/` directory will be copied as-is to the output
build directory.

### `before_render(renderer)`

A theme directory may  contain a Node.py source file with the `.yassg-theme.py`
suffix. This file will be be loaded and the function `before_render()` will be
called before the theme is rendered. This function can be used to
pre-process the configuration, pages or Jinja2 environment.

## Available Built-ins

### `config`

The `.yassg.toml` configuration file as dictionary.

### `renderer`

The `Renderer` object that is currently executing the rendering process.

### `page`

The `Page` that is currently being rendered.

### `Markdown()`

A factory returning a `markdown.Markdown` object that can be used to convert
the contents of a page. At the beginning of a `page.html` template, you
might want to use the following two lines:

```python
{%- set md = Markdown() -%}
{%- set content = md.convert(renderer.current_page.content) -%}
```

### `url_for(path:Union[str,Page])`

Returns a URL relative to the current page pointing to the specified *path*,
which is either a string (thus, a specific file in the site's final directory)
or a `Page` object referencing another page.

Examples:

```html
<link rel="stylesheet" href="\{{ url_for('static/style.css') }}">

<div class="nav navbar">
  {% for other_page in renderer.pages %}
    <a class="item" href="\{{ url_for(page) }}">{{ other_page.detail('title', page.name) }}</a>
  {% endif %}
</div>
```
