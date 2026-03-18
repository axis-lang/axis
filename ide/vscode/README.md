# Axis VS Code Support

This directory contains the first VS Code editor support package for Axis.

Current features:

- `*.ax` file association
- syntax highlighting
- Markdown-style doc block highlighting for `---` sections
- comments, bracket pairing, and simple indentation rules
- snippets for common Axis blocks and declarations

This iteration is intentionally editor-only. It does not include:

- diagnostics
- hover
- go to definition
- semantic completion
- language server support

Design alignment:

- Block structure, snippets, and indentation are aligned with `src/axis/syn/outline.py`.
- Expression/operator highlighting is aligned with `src/axis/syn/grammar/Axis.g4`.

Doc block behavior:

- A line that contains `---` starts a documentation block.
- The block content is highlighted as Markdown.
- The editor returns to Axis highlighting when the next outline-style Axis keyword is found.
- This is a best-effort editor rule for now; exact outline-level validation is planned for a future `axis-lsp` iteration.

## Install locally in VS Code

1. Open VS Code.
2. Open `ide/vscode/` as the extension workspace.
3. Use `Developer: Install Extension from Location...` and select `ide/vscode/`, or package it as a VSIX later.
4. Reload VS Code and open any `*.ax` file.

## Next step

The intended next iteration is `axis-lsp`, which will provide diagnostics and semantic editor features on top of this baseline.
