# Convert HTML to markdown

...and other stuff like that.

There are several utilities and libraries that can help you convert HTML to GitHub Wiki style Markdown efficiently. Here are a couple of options you can use in Python and Bash:

## Python Utility

1. **`markdownify` Library**:

   * This Python library converts HTML to Markdown. It's simple to use and produces clean output.

   **Installation**:

   ```bash
   pip install markdownify
   ```

   **Usage**:

   ```python
   from markdownify import markdownify as md

   html_content = """
   <h1>This is a Title</h1>
   <p>This is a paragraph with <strong>bold text</strong>.</p>
   """
   markdown_content = md(html_content)
   print(markdown_content)
   ```

2. **`html2text` Library**:

   * Another Python library that converts HTML to Markdown format.

   **Installation**:

   ```bash
   pip install html2text
   ```

   **Usage**:

   ```python
   import html2text

   html_content = "<h1>This is a Title</h1><p>This is a paragraph.</p>"
   markdown_content = html2text.html2text(html_content)
   print(markdown_content)
   ```

### Bash Utility

3. **Pandoc**:

   * Pandoc is a powerful command-line tool that can convert between various document formats, including HTML to Markdown.

   **Installation**:

   ```bash
   # For Debian/Ubuntu
   sudo apt-get install pandoc

   # For macOS (using Homebrew)
   brew install pandoc
   ```

   **Usage**:

   ```bash
   pandoc -f html -t markdown -o output.md input.html
   ```

### Summary

* For Python, `markdownify` and `html2text` are great libraries for converting HTML to Markdown.
* For a command-line solution, `pandoc` is a robust tool that handles a wide variety of document conversions, including HTML to GitHub-compatible Markdown.

Choose the method that best fits your workflow! If you need any specific help with these tools, feel free to ask!

---

`pandoc` is definitely the wizard's wand
