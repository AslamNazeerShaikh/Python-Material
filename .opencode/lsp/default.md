---
name: default
description: LSP configuration for Python-Material (Python 3.14 study + practice)
version: 1.0.0
enabled: true
servers:
  # Python Language Server (pyright - fast, type-aware)
  - name: pyright
    command: pyright-langserver
    args:
      - --stdio
    filetypes:
      - python
    rootPatterns:
      - "pyproject.toml"
      - "setup.cfg"
      - ".venv"

  # Ruff LSP (lint + format diagnostics)
  - name: ruff
    command: ruff
    args:
      - server
    filetypes:
      - python
    rootPatterns:
      - "pyproject.toml"
      - "ruff.toml"

  # JSON Language Server (opencode.json, configs)
  - name: json-language-server
    command: vscode-json-language-server
    args:
      - --stdio
    filetypes:
      - json
    rootPatterns:
      - package.json

settings:
  # General settings
  completion:
    triggerCharacters: [".", ":", "<", "@", "#"]
    resolveTimeout: 5000

  diagnostics:
    enable: true
    debounce: 300

  # Python specific settings
  python:
    formatting:
      enable: true
      indentSize: 4
      tabSize: 4
      useTabs: false
      newLine: "\n"
    completion:
      triggerCharacters: [".", "(", "@", "#"]
      provideRegexCompletion: true
    diagnostics:
      enable: true
      enableSuppress: true
    inlayHints:
      enable: true
      parameterNames: true
      typeAnnotations: true
    navigation:
      enable: true
