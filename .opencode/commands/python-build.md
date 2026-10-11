---
name: python-build
description: Byte-compile sources and install the package editable (Python-Material)
category: build
command: python -m compileall src && pip install -e ".[dev]"
examples:
  - python -m compileall src
  - pip install -e ".[dev]"
