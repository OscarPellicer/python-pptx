# This is a fork of python-pptx with MathML parsing and LaTeX conversion

A significant experimental feature has been added to enable the parsing of MathML (specifically ``<a14:m>`` elements containing either ``<m:oMathPara>`` for block equations or ``<m:oMath>`` for inline equations) embedded within PowerPoint files. This MathML content can then be converted into LaTeX strings.

This functionality allows for the extraction of mathematical equations from slides. When a presentation is parsed, these math elements are represented as special run objects. The LaTeX representation of the math equation can be accessed via the ``.text`` property of such a run (e.g., a math run might return a string like ``'$x^2 + y^2 = z^2$'``).

Unrelated to the MathML parsing, this fork also fixes the parsing of tiff images.

**Important note:** Though the fork is right now passing all tests (except txt-font-props.feature:Get Font.underline, tested only on Python 3.10 and 3.11), this fork is still experimental and it is not yet ready for production use! Also, no tests or documentation have been added for the new features. Please report any issues in the issue tracker for this fork!

This was developed while I was working on [pptx2marp](https://github.com/OscarPellicer/pptx2marp), a tool that converts PowerPoint presentations to Marp markdown, itself a fork of [ssine/pptx2md](https://github.com/ssine/pptx2md), and I needed to parse the MathML in the presentations, as well as fix the parsing of tiff images.

# python-pptx

*python-pptx* is a Python library for creating, reading, and updating PowerPoint (.pptx) files.

A typical use would be generating a PowerPoint presentation from dynamic content such as a database query, analytics output, or a JSON payload, perhaps in response to an HTTP request and downloading the generated PPTX file in response. It runs on any Python capable platform, including macOS and Linux, and does not require the PowerPoint application to be installed or licensed.

It can also be used to analyze PowerPoint files from a corpus, perhaps to extract search indexing text, images, and now, mathematical equations.

Furthermore, it can automate the production of slides that would be tedious to create by hand.

## More Information

More information is available in the [python-pptx documentation](https://python-pptx.readthedocs.org/en/latest/).

Browse [examples with screenshots](https://python-pptx.readthedocs.org/en/latest/user/quickstart.html) to get a quick idea of what you can do with python-pptx.