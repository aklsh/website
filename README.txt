check here 🡒 https://aklsh.me

Build
-----

Requires Hugo Extended, Python 3, make, and md2gemini (install with
`uv tool install md2gemini` or `pipx install md2gemini`). Deployment uses rsync.

The Markdown files in content/ are the single source of truth for both
publishing targets.  `make build` renders them with Hugo to public/ and
converts them to the Gemini capsule in public-gemini/ with md2gemini.

Use `make http` or `make gemini` to build one target, and `make deploy` to
build and deploy both targets.

`public-gemini/` is a complete Gemini capsule: every page is a generated
`.gmi` file with root-relative links. Images and other large media stay on
the HTTPS CDN and are linked from the gemtext. Point agate's `--content` at
the deployed directory to serve it.
