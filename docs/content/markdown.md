+++
title = "Markdown Features"
+++

Yassg allows you to plug in preprocessors for the markdown in your files.
The default preprocessor, `"yassg:preprocess"`, brings various new syntaxes
to the table.

## References

References to other pages can be specified enclsoed in two brackets.
Example:

    Also, be sure to check out the documentation about \[[theming]]. The
    \[[Usage page]](usage) also has interesting information.

Renders as

> Also, be sure to check out the documentation about [[theming]]. The
> [[Usage page]](usage) also has interesting information.

## Shortcodes

Shortcodes can be defined by a theme, but also by your site in the
`shortcodes/` directory or in the `shortcodes.py` Python script. Shortcodes
in HTML can make use of the Jinja2 templating engine. To use shortcodes in
your Markdown page, you wrap the call to the shortcode Jinja2-style:

    \{{ gist(user="defunkt", id="2059") }}

HTML Example:

```html
<!-- shortcodes/gist.html -->
{% set suffix = ('?file=' + file) if file else '' %}
<script src="https://gist.github.com/{{user}}/{{id}}{{suffix}}.js"></script>
```

Python Example:

```python
def gist(user, id, file=None):
  return '<script src="https://gist.github.com/{user}/{id}{suffix}.js"></script>'\
    .format(user=user, id=id, suffix=('?file=' + file) if file else '')
```

### Built-in shortcodes

#### `gist(user, id, file)`

Embedd a GitHub Gist.
