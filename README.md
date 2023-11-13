# Gerador de Token para API da TD Ameritrade

## Modo Dev

1. `poetry install`

2. `poetry run python -m app`

## Modo Prod

`poetry run pyinstaller app/__main__.py`

---

- Fix `qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.`

  ```bash
  sudo apt install libxcb-*
  ```
