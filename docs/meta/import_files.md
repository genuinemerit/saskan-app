# from importlib.resources import files

The modern way (since Python 3.9) to access package data files (like our YAMLs).

files("saskan.data.locales").joinpath("es-ES/messages.yaml") gives us a pathlib.Path-like object that works whether the package is unpacked on disk or inside a zip/wheel.

Why not just use Path? Because Path assumes the file is on the real filesystem. Once we install our package from a wheel, those files may live inside a zip — Path would break, but importlib.resources still works.

That’s why we explicitly build the wheel and sanity-check it: confirms these resources will resolve correctly.

---

## wheel check code

This example proves that the "locales" files are getting included in the wheel.

```bash
poetry build
pip install dist/*.whl --force-reinstall
python -c "from importlib.resources import files; print(list(files('saskan.data.locales').iterdir()))"
```
