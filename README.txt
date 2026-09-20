check here 🡒 https://aklsh.me

Build
-----

Requires Hugo Extended, Python 3, make, and md2gemini (install with
`uv tool install md2gemini` or `pipx install md2gemini`). Deployment uses rsync.

The Markdown files in content/ are the single source of truth for both
publishing targets.  `make build` first creates disposable, target-specific
Markdown trees in .build/mdhtml/ and .build/mdgemtext/.  Hugo reads the first
tree and scripts/build-gemini.py converts the second tree to public-gemini/.

Use `make http` or `make gemini` to build one target, and `make deploy` to
build and deploy both targets.

When a page needs target-specific content, use HTML comments in its Markdown:

    <!-- IF HTML -->
    HTML-only content, including raw HTML or Hugo shortcodes
    <!-- ENDIF -->

    <!-- IF GEMTEXT -->
    Gemini-only content
    <!-- ENDIF -->

The markers are removed during preparation.  The HTML-only block therefore
reaches Hugo, while the Gemini-only block reaches md2gemini.  `GEMINI` is
accepted as an alias for `GEMTEXT`.
