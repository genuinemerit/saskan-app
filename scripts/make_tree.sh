#! bash
tree -a -I '.git|.mypy_cache|.pytest_cache|__pycache__|.venv|.direnv|dist|build' -L 4 > tree.txt
